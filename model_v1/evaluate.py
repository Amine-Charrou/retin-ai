import torch
from torch.utils.data import DataLoader
import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix, cohen_kappa_score
import argparse
import os

# Importations locales
from dataset import RetinAIDataset, get_valid_transforms
from model import RetinAIModel
from loss import OrdinalTargetEncoder

def compute_clinical_metrics(targets, predictions):
    """
    Calcule des métriques orientées clinique pour l'ophtalmologie :
    1. Quadratic Weighted Kappa (QWK)
    2. Sensibilité et Spécificité pour la "Referable DR" (Stades 2, 3, 4)
       La Referable DR est le seuil à partir duquel le patient doit impérativement 
       être envoyé en consultation ophtalmologique spécialisée.
    """
    targets = np.array(targets)
    predictions = np.array(predictions)
    
    # 1. Calcul du QWK
    qwk = cohen_kappa_score(targets, predictions, weights='quadratic')
    
    # 2. Conversion en classe binaire "Referable DR" (stade >= 2)
    binary_targets = (targets >= 2).astype(int)
    binary_preds = (predictions >= 2).astype(int)
    
    # Calcul de la matrice de confusion binaire
    # TN, FP, FN, TP
    tn, fp, fn, tp = confusion_matrix(binary_targets, binary_preds).ravel()
    
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    
    return {
        "qwk": qwk,
        "referable_sensitivity": sensitivity,
        "referable_specificity": specificity,
        "confusion_matrix": confusion_matrix(targets, predictions)
    }

def main():
    parser = argparse.ArgumentParser(description="Script d'évaluation clinique RetinAI")
    parser.add_argument('--model_path', type=str, default='best_model_fold_1.pth', help="Chemin du checkpoint .pth")
    parser.add_argument('--csv_path', type=str, required=True, help="Chemin du CSV d'annotations de validation")
    parser.add_argument('--img_dir', type=str, required=True, help="Dossier contenant les images")
    parser.add_argument('--model_name', type=str, default='efficientnet_b4', help="Nom du backbone")
    parser.add_argument('--image_size', type=int, default=512, help="Taille des images")
    parser.add_argument('--batch_size', type=int, default=4, help="Taille du batch")
    
    args = parser.parse_args()
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Évaluation sur le périphérique : {device}")
    
    # 1. Vérifier si le modèle existe
    if not os.path.exists(args.model_path):
        raise FileNotFoundError(f"Checkpoint introuvable sous : {args.model_path}")
        
    # 2. Charger les données
    df = pd.read_csv(args.csv_path)
    
    dataset = RetinAIDataset(
        df, args.img_dir, 
        transform=get_valid_transforms(args.image_size), 
        image_size=args.image_size
    )
    dataloader = DataLoader(
        dataset, batch_size=args.batch_size, 
        shuffle=False, num_workers=0
    )
    
    # 3. Charger le modèle
    model = RetinAIModel(model_name=args.model_name, pretrained=False, num_classes=5)
    model.load_state_dict(torch.load(args.model_path, map_location=device))
    model = model.to(device)
    model.eval()
    
    all_targets = []
    all_predictions = []
    
    print("Inférence sur le dataset d'évaluation...")
    with torch.no_grad():
        for images, labels in dataloader:
            images = images.to(device)
            logits = model(images)
            
            # Décoder les sorties ordinales
            preds = OrdinalTargetEncoder.decode(logits)
            
            all_targets.extend(labels.numpy())
            all_predictions.extend(preds.cpu().numpy())
            
    # 4. Calcul des performances
    metrics = compute_clinical_metrics(all_targets, all_predictions)
    
    print("\n================ RAPPORT D'ÉVALUATION CLINIQUE ================")
    print(f"Quadratic Weighted Kappa (QWK) : {metrics['qwk']:.4f}")
    print(f"Sensibilité (Referable DR, Stade >= 2) : {metrics['referable_sensitivity']:.2%} (Seuil acceptable: >= 95.0%)")
    print(f"Spécificité (Referable DR, Stade >= 2) : {metrics['referable_specificity']:.2%} (Seuil acceptable: >= 85.0%)")
    
    print("\nMatrice de Confusion des Stades (0 à 4) :")
    print(metrics['confusion_matrix'])
    
    print("\nRapport de Classification Détaillé :")
    print(classification_report(all_targets, all_predictions, target_names=[
        "Stade 0 - Aucun",
        "Stade 1 - Léger",
        "Stade 2 - Modéré",
        "Stade 3 - Sévère",
        "Stade 4 - Prolifératif"
    ], zero_division=0))
    print("================================================================")

if __name__ == "__main__":
    # Si exécuté seul sans argument, afficher une explication
    try:
        main()
    except Exception as e:
        print(f"Note : Script configuré pour exécution en ligne de commande. Erreur : {e}")
        print("Usage: python evaluate.py --csv_path <path> --img_dir <path> --model_path <path>")
