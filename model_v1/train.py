import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torch.optim.lr_scheduler import CosineAnnealingLR
import pandas as pd
import numpy as np
import os
import argparse
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import cohen_kappa_score, classification_report
import shutil
import cv2

# Importations des modules locaux
from preprocess import preprocess_fundus_image
from dataset import RetinAIDataset, get_train_transforms, get_valid_transforms
from loss import OrdinalFocalLoss, OrdinalTargetEncoder
from model import RetinAIModel

# Essayer d'importer les outils de tracking (MLOps)
try:
    import wandb
    WANDB_AVAILABLE = True
except ImportError:
    WANDB_AVAILABLE = False

try:
    import mlflow
    import mlflow.pytorch
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False

def seed_everything(seed=42):
    """
    Assure la reproductibilité totale des résultats de l'entraînement.
    """
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

def calculate_qwk(targets, predictions):
    """
    Calcule le score Quadratic Weighted Kappa (QWK) de Cohen.
    C'est la métrique décisive pour évaluer la qualité du dépistage ordinale.
    """
    return cohen_kappa_score(targets, predictions, weights='quadratic')

def train_one_epoch(model, dataloader, criterion, optimizer, scheduler, device):
    model.train()
    running_loss = 0.0
    all_targets = []
    all_predictions = []
    
    for images, labels in dataloader:
        images = images.to(device)
        labels = labels.to(device)
        
        optimizer.zero_grad()
        
        # Propagation avant (forward)
        logits = model(images)
        loss = criterion(logits, labels)
        
        # Rétropropagation (backward)
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item() * images.size(0)
        
        # Décoder les prédictions ordinales pour calculer le QWK d'entraînement
        preds = OrdinalTargetEncoder.decode(logits)
        all_targets.extend(labels.cpu().numpy())
        all_predictions.extend(preds.cpu().numpy())
        
    scheduler.step()
    
    epoch_loss = running_loss / len(dataloader.dataset)
    epoch_qwk = calculate_qwk(all_targets, all_predictions)
    
    return epoch_loss, epoch_qwk

@torch.no_grad()
def validate(model, dataloader, criterion, device):
    model.eval()
    running_loss = 0.0
    all_targets = []
    all_predictions = []
    
    for images, labels in dataloader:
        images = images.to(device)
        labels = labels.to(device)
        
        logits = model(images)
        loss = criterion(logits, labels)
        
        running_loss += loss.item() * images.size(0)
        
        # Décoder les prédictions
        preds = OrdinalTargetEncoder.decode(logits)
        all_targets.extend(labels.cpu().numpy())
        all_predictions.extend(preds.cpu().numpy())
        
    val_loss = running_loss / len(dataloader.dataset)
    val_qwk = calculate_qwk(all_targets, all_predictions)
    
    return val_loss, val_qwk, all_targets, all_predictions

def run_fold(fold, train_df, val_df, img_dir, args, device):
    print(f"\n========== DÉBUT DU FOLD {fold+1} / {args.n_splits} ==========")
    
    # 1. Datasets & Dataloaders
    train_dataset = RetinAIDataset(
        train_df, img_dir, 
        transform=get_train_transforms(args.image_size), 
        image_size=args.image_size
    )
    val_dataset = RetinAIDataset(
        val_df, img_dir, 
        transform=get_valid_transforms(args.image_size), 
        image_size=args.image_size
    )
    
    train_loader = DataLoader(
        train_dataset, batch_size=args.batch_size, 
        shuffle=True, num_workers=args.num_workers, pin_memory=True
    )
    val_loader = DataLoader(
        val_dataset, batch_size=args.batch_size, 
        shuffle=False, num_workers=args.num_workers, pin_memory=True
    )
    
    # 2. Modèle, Perte & Optimiseur
    model = RetinAIModel(model_name=args.model_name, pretrained=args.pretrained, num_classes=5)
    model = model.to(device)
    
    criterion = OrdinalFocalLoss(num_classes=5, alpha=args.alpha, gamma=args.gamma)
    optimizer = optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    scheduler = CosineAnnealingLR(optimizer, T_max=args.epochs, eta_min=1e-6)
    
    # 3. Initialisation de Weights & Biases (W&B)
    if args.use_wandb and WANDB_AVAILABLE:
        wandb.init(
            project="RetinAI-Diabetic-Retinopathy",
            name=f"Fold_{fold+1}_{args.model_name}",
            config={
                "fold": fold + 1,
                "model": args.model_name,
                "epochs": args.epochs,
                "lr": args.lr,
                "batch_size": args.batch_size,
                "loss": "OrdinalFocalLoss",
                "image_size": args.image_size
            },
            reinit=True
        )
        
    best_qwk = -1.0
    best_loss = float('inf')
    
    # 4. Boucle d'Époques
    for epoch in range(args.epochs):
        train_loss, train_qwk = train_one_epoch(
            model, train_loader, criterion, optimizer, scheduler, device
        )
        val_loss, val_qwk, targets, preds = validate(
            model, val_loader, criterion, device
        )
        
        print(f"Époque {epoch+1:02d}/{args.epochs:02d} | "
              f"Train Loss: {train_loss:.4f} (QWK: {train_qwk:.4f}) | "
              f"Val Loss: {val_loss:.4f} (QWK: {val_qwk:.4f})")
              
        # Logger sur W&B
        if args.use_wandb and WANDB_AVAILABLE:
            wandb.log({
                "epoch": epoch + 1,
                "train_loss": train_loss,
                "train_qwk": train_qwk,
                "val_loss": val_loss,
                "val_qwk": val_qwk,
                "lr": optimizer.param_groups[0]['lr']
            })
            
        # Sauvegarde du meilleur modèle (basé sur le score QWK clinique de validation)
        if val_qwk > best_qwk:
            best_qwk = val_qwk
            best_loss = val_loss
            model_path = f"best_model_fold_{fold+1}.pth"
            torch.save(model.state_code() if hasattr(model, 'state_code') else model.state_dict(), model_path)
            print(f"--> Nouveau record de QWK ! Modèle sauvegardé sous : {model_path}")
            
    print(f"========== FIN DU FOLD {fold+1} : Meilleur QWK = {best_qwk:.4f} ==========")
    if args.use_wandb and WANDB_AVAILABLE:
        wandb.finish()
        
    return best_qwk, best_loss

def generate_dummy_data(temp_dir="dummy_dataset", n_samples=20):
    """
    Génère un faux jeu de données (images de fond d'œil + fichier CSV)
    pour valider que l'intégralité du script tourne sans bug sur CPU en local.
    """
    print(f"Génération d'un jeu de données de test ({n_samples} images)...")
    os.makedirs(temp_dir, exist_ok=True)
    
    img_names = []
    diagnoses = []
    
    for i in range(n_samples):
        # 1. Créer une image noire
        img = np.zeros((400, 400, 3), dtype=np.uint8)
        # 2. Dessiner un disque orange représentant la rétine
        cv2.circle(img, (200, 200), 160, (15, 80, 220), -1)
        # 3. Dessiner la papille optique (disque jaune)
        cv2.circle(img, (230, 180), 20, (120, 210, 255), -1)
        
        # Assigner une classe aléatoire entre 0 (Sain) et 4 (Prolifératif)
        diagnosis = np.random.randint(0, 5)
        
        # Ajouter quelques taches rouges pour simuler des hémorragies dans les cas DR
        if diagnosis >= 2:
            cv2.circle(img, (180, 220), 4, (0, 0, 180), -1)
            cv2.circle(img, (150, 190), 3, (0, 0, 150), -1)
            
        img_name = f"scan_{i}.png"
        cv2.imwrite(os.path.join(temp_dir, img_name), img)
        
        img_names.append(f"scan_{i}")
        diagnoses.append(diagnosis)
        
    # Créer le CSV associé
    df = pd.DataFrame({
        'image_id': img_names,
        'diagnosis': diagnoses
    })
    csv_path = os.path.join(temp_dir, "train_labels.csv")
    df.to_csv(csv_path, index=False)
    
    print(f"[OK] Faux jeu de donnees cree avec succes dans : {temp_dir}/")
    return csv_path, temp_dir

def main():
    parser = argparse.ArgumentParser(description="Script d'entraînement RetinAI")
    # Configuration des dossiers
    parser.add_argument('--csv_path', type=str, default=None, help="Chemin du CSV d'annotations")
    parser.add_argument('--img_dir', type=str, default=None, help="Chemin du dossier d'images")
    parser.add_argument('--dummy', action='store_true', default=False, help="Génère et s'entraîne sur un faux jeu de données (Test CPU)")
    
    # Hyperparamètres d'entraînement
    parser.add_argument('--model_name', type=str, default='efficientnet_b4', help="Backbone timm à utiliser")
    parser.add_argument('--pretrained', action='store_true', default=True, help="Charger les poids pré-entraînés ImageNet")
    parser.add_argument('--image_size', type=int, default=512, help="Taille des images d'entrée")
    parser.add_argument('--epochs', type=int, default=10, help="Nombre d'époques par fold")
    parser.add_argument('--batch_size', type=int, default=4, help="Taille du batch")
    parser.add_argument('--lr', type=float, default=3e-4, help="Learning rate initial")
    
    # Paramètres de validation & perte
    parser.add_argument('--n_splits', type=int, default=5, help="Nombre de plis pour la cross-validation")
    parser.add_argument('--alpha', type=float, default=0.25, help="Alpha pour la Focal Loss")
    parser.add_argument('--gamma', type=float, default=2.0, help="Gamma pour la Focal Loss")
    
    # MLOps et performances
    parser.add_argument('--use_wandb', action='store_true', default=False, help="Activer le tracking Weights & Biases")
    parser.add_argument('--use_mlflow', action='store_true', default=False, help="Activer le tracking MLflow")
    parser.add_argument('--num_workers', type=int, default=0, help="Nombre de workers PyTorch")
    
    args = parser.parse_args()
    seed_everything(42)
    
    # Gérer l'entraînement sur le faux jeu de données local (Dummy mode)
    is_dummy_created = False
    if args.dummy or (args.csv_path is None or args.img_dir is None):
        print("[DUMMY MODE] Aucun chemin valide spécifié ou flag --dummy actif.")
        print("Nous allons générer un jeu de données factice et exécuter un test CPU rapide...")
        args.dummy = True
        args.pretrained = False # Pas besoin de télécharger de gros poids ImageNet pour un simple test
        args.epochs = 2         # Juste 2 époques de test
        args.n_splits = 2       # Juste 2 folds pour aller vite
        args.batch_size = 2
        csv_path, img_dir = generate_dummy_data()
        is_dummy_created = True
    else:
        csv_path = args.csv_path
        img_dir = args.img_dir
        
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Périphérique utilisé pour l'entraînement : {device}")
    
    # Charger le fichier CSV d'annotations
    df = pd.read_csv(csv_path)
    
    # Détecter la colonne label
    label_col = None
    for col in ['diagnosis', 'level', 'label', 'target']:
        if col in df.columns:
            label_col = col
            break
    if label_col is None:
        label_col = df.columns[1]
        
    print(f"Distribution des classes initiales :")
    print(df[label_col].value_counts().sort_index())
    
    # Découpage Stratified 5-Fold
    skf = StratifiedKFold(n_splits=args.n_splits, shuffle=True, random_state=42)
    fold_metrics = []
    
    # Initialiser MLflow
    if args.use_mlflow and MLFLOW_AVAILABLE:
        mlflow.set_experiment("RetinAI_Training")
        mlflow.start_run(run_name=f"Run_{args.model_name}")
        mlflow.log_params({
            "model": args.model_name,
            "image_size": args.image_size,
            "epochs": args.epochs,
            "lr": args.lr,
            "batch_size": args.batch_size,
            "loss": "OrdinalFocalLoss"
        })
        
    # Lancement des Folds
    for fold, (train_idx, val_idx) in enumerate(skf.split(df, df[label_col])):
        train_df = df.iloc[train_idx]
        val_df = df.iloc[val_idx]
        
        qwk, loss = run_fold(fold, train_df, val_df, img_dir, args, device)
        fold_metrics.append((qwk, loss))
        
        # Enregistrer les métriques sur MLflow pour chaque fold
        if args.use_mlflow and MLFLOW_AVAILABLE:
            mlflow.log_metric(f"fold_{fold+1}_best_qwk", qwk)
            mlflow.log_metric(f"fold_{fold+1}_best_loss", loss)
            
    # Calculer et afficher les performances finales agrégées de la cross-validation
    avg_qwk = np.mean([m[0] for m in fold_metrics])
    avg_loss = np.mean([m[1] for m in fold_metrics])
    
    print("\n================ ÉVALUATION FINALE CROSS-VALIDATION ================")
    print(f"Moyenne de QWK sur {args.n_splits} folds : {avg_qwk:.4f}")
    print(f"Moyenne de Perte sur {args.n_splits} folds : {avg_loss:.4f}")
    print("====================================================================")
    
    if args.use_mlflow and MLFLOW_AVAILABLE:
        mlflow.log_metric("cv_mean_qwk", avg_qwk)
        mlflow.log_metric("cv_mean_loss", avg_loss)
        
        # Logger le modèle final du premier fold dans le catalogue MLflow
        if os.path.exists("best_model_fold_1.pth"):
            # Enregistrer le fichier de poids dans MLflow
            mlflow.log_artifact("best_model_fold_1.pth")
            
        mlflow.end_run()
        
    # Nettoyage automatique du faux jeu de données
    if is_dummy_created and os.path.exists(img_dir):
        print("Nettoyage du jeu de données factice...")
        shutil.rmtree(img_dir)
        print("[OK] Nettoyage reussi.")

if __name__ == "__main__":
    main()
