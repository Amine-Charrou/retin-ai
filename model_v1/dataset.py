import torch
from torch.utils.data import Dataset
import pandas as pd
import numpy as np
import cv2
import os
from preprocess import preprocess_fundus_image

try:
    import albumentations as A
    from albumentations.pytorch import ToTensorV2
    ALBUMENTATIONS_AVAILABLE = True
except ImportError:
    ALBUMENTATIONS_AVAILABLE = False
    print("Note : Albumentations n'est pas installe. Utilisation du repli manuel PyTorch pour la normalisation.")

def get_train_transforms(image_size=512):
    """
    Définit les augmentations de données robustes avec Albumentations
    pour lutter contre le surapprentissage sur les datasets de petite taille.
    """
    if ALBUMENTATIONS_AVAILABLE:
        return A.Compose([
            A.HorizontalFlip(p=0.5),
            A.VerticalFlip(p=0.5),
            A.RandomRotate90(p=0.5),
            A.ShiftScaleRotate(
                shift_limit=0.05, 
                scale_limit=0.1, 
                rotate_limit=180, 
                border_mode=cv2.BORDER_CONSTANT, 
                value=0, 
                p=0.7
            ),
            A.RandomBrightnessContrast(
                brightness_limit=0.1, 
                contrast_limit=0.1, 
                p=0.5
            ),
            A.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
                max_pixel_value=255.0,
            ),
            ToTensorV2()
        ])
    else:
        # Solution de repli locale sans albumentations
        return "manual_fallback"

def get_valid_transforms(image_size=512):
    """
    Transformations simples pour la validation et le test (uniquement normalisation).
    """
    if ALBUMENTATIONS_AVAILABLE:
        return A.Compose([
            A.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
                max_pixel_value=255.0,
            ),
            ToTensorV2()
        ])
    else:
        # Solution de repli locale sans albumentations
        return "manual_fallback"

class RetinAIDataset(Dataset):
    """
    Classe Dataset PyTorch personnalisée pour le chargement des images de fond d'œil.
    Elle intègre automatiquement notre pipeline de prétraitement clinique.
    """
    def __init__(self, df, img_dir, transform=None, is_test=False, image_size=512, sigma=10):
        """
        Args:
            df (pd.DataFrame): DataFrame contenant les chemins/ID des images et les labels.
            img_dir (str): Répertoire racine contenant les images.
            transform (A.Compose): Pipeline d'augmentations Albumentations.
            is_test (bool): Si Vrai, n'attend pas de colonne de label (mode prédiction).
            image_size (int): Taille finale des images (512x512).
            sigma (int): Rayon gaussien pour le prétraitement Ben Graham.
        """
        self.df = df.reset_index(drop=True)
        self.img_dir = img_dir
        self.transform = transform
        self.is_test = is_test
        self.image_size = image_size
        self.sigma = sigma
        
        # Détection automatique de la colonne contenant l'identifiant de l'image
        # (Supporte les formats courants de APTOS/Kaggle : 'image_id', 'image', 'id_code')
        self.image_col = None
        for col in ['image_id', 'image', 'id_code', 'id']:
            if col in self.df.columns:
                self.image_col = col
                break
        if self.image_col is None:
            self.image_col = self.df.columns[0] # Fallback sur la première colonne
            
        # Détection de la colonne du label de diagnostic (0 à 4)
        if not self.is_test:
            self.label_col = None
            for col in ['diagnosis', 'level', 'label', 'target']:
                if col in self.df.columns:
                    self.label_col = col
                    break
            if self.label_col is None:
                self.label_col = self.df.columns[1] # Fallback sur la deuxième colonne

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        # 1. Obtenir le nom du fichier et construire le chemin absolu
        img_name = str(self.df.loc[idx, self.image_col])
        # Ajouter l'extension .png si elle n'est pas déjà présente dans le CSV
        if not img_name.endswith(('.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG')):
            img_path = os.path.join(self.img_dir, img_name + '.png')
        else:
            img_path = os.path.join(self.img_dir, img_name)
            
        # 2. Charger et appliquer le pipeline de prétraitement clinique
        # (Si l'image n'existe pas, on renvoie une matrice de secours ou lève l'erreur)
        try:
            # Cette fonction applique crop_retina + Ben Graham + CLAHE + resize intermédiaire
            image_preprocessed = preprocess_fundus_image(
                img_path, 
                target_size=self.image_size, 
                sigma=self.sigma
            )
        except Exception as e:
            # Fallback en cas de fichier manquant ou corrompu durant l'entraînement :
            # Renvoie une image noire pour éviter de faire crasher l'entraînement
            # (Il vaut mieux logger un avertissement)
            print(f"Avertissement : Erreur lors du chargement de {img_path} ({e})")
            image_preprocessed = np.zeros((self.image_size, self.image_size, 3), dtype=np.uint8)

        # OpenCV charge les images en BGR, convertissons en RGB pour Albumentations et timm
        image_preprocessed = cv2.cvtColor(image_preprocessed, cv2.COLOR_BGR2RGB)

        # 3. Appliquer les augmentations et la normalisation d'imagerie
        if self.transform and self.transform != "manual_fallback":
            augmented = self.transform(image=image_preprocessed)
            image_tensor = augmented['image']
        else:
            # Solution de repli manuelle (conversion HWC -> CHW normalisée ImageNet)
            image_float = image_preprocessed.astype(np.float32) / 255.0
            mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
            std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
            image_normalized = (image_float - mean) / std
            image_tensor = torch.tensor(image_normalized, dtype=torch.float32).permute(2, 0, 1)

        # 4. Retourner le couple (Image, Label) ou juste l'image si c'est pour l'inférence
        if self.is_test:
            return image_tensor
        else:
            label = int(self.df.loc[idx, self.label_col])
            return image_tensor, torch.tensor(label, dtype=torch.long)

# Test unitaire rapide du Dataset
if __name__ == "__main__":
    print("Test du Dataset PyTorch RetinAI...")
    # Créer un DataFrame factice
    dummy_df = pd.DataFrame({
        'image_id': ['img_1', 'img_2'],
        'diagnosis': [0, 4]
    })
    
    # Créer des fichiers temporaires pour le test
    os.makedirs("dummy_images", exist_ok=True)
    for name in ['img_1.png', 'img_2.png']:
        dummy_img = np.zeros((300, 300, 3), dtype=np.uint8)
        cv2.circle(dummy_img, (150, 150), 100, (20, 100, 220), -1)
        cv2.imwrite(os.path.join("dummy_images", name), dummy_img)
        
    try:
        transforms = get_train_transforms(image_size=512)
        dataset = RetinAIDataset(dummy_df, "dummy_images", transform=transforms)
        
        print(f"Nombre d'elements dans le dataset : {len(dataset)}")
        img_tensor, label = dataset[0]
        print(f"[OK] Succes ! Forme du tenseur image : {img_tensor.shape}")
        print(f"[OK] Type du tenseur : {img_tensor.dtype}")
        print(f"[OK] Classe cible : {label.item()} (Type: {label.dtype})")
    except Exception as e:
        print(f"[ERROR] Erreur lors du test du dataset : {e}")
    finally:
        # Nettoyage
        import shutil
        if os.path.exists("dummy_images"):
            shutil.rmtree("dummy_images")
