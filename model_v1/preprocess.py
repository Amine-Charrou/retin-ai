import cv2
import numpy as np
import os

def crop_retina_circle(image, tolerance=10):
    """
    Détecte les contours de la rétine et effectue un rognage circulaire ou rectangulaire serré
    pour éliminer le fond noir inutile et centrer la zone d'intérêt.
    """
    if len(image.shape) == 2:
        gray = image
    else:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
    # Seuil pour séparer le fond noir de la rétine éclairée
    _, thresh = cv2.threshold(gray, tolerance, 255, cv2.THRESH_BINARY)
    
    # Trouver les contours de la zone éclairée
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        # Si aucun contour n'est détecté, retourner l'image originale
        return image
        
    # Sélectionner le plus grand contour (la rétine)
    c = max(contours, key=cv2.contourArea)
    
    # Obtenir la boîte englobante
    x, y, w, h = cv2.boundingRect(c)
    
    # Rognage de la boîte englobante
    cropped = image[y:y+h, x:x+w]
    return cropped

def ben_graham_preprocessing(image, sigma=10):
    """
    Implémente la célèbre méthode de Ben Graham (gagnant Kaggle 2015) :
    Soustraction de la couleur locale floutée pour harmoniser l'éclairage et
    faire ressortir les lésions microscopiques (microanévrysmes, exsudats).
    """
    # Éviter de modifier l'image originale
    img = image.copy()
    
    # Appliquer un flou gaussien de rayon sigma pour capturer l'éclairage global
    blurred = cv2.GaussianBlur(img, (0, 0), sigma)
    
    # Soustraire le flou de l'image d'origine pour enlever la basse fréquence d'éclairage
    # Formule : 4 * img - 4 * blurred + 128 (gris neutre de base)
    processed = cv2.addWeighted(img, 4, blurred, -4, 128)
    
    return processed

def apply_clahe(image, clip_limit=2.0, tile_grid_size=(8, 8)):
    """
    Applique l'égalisation adaptative de contraste CLAHE sur le canal L de l'espace LAB
    afin de rehausser les vaisseaux et microanévrysmes sans surexposer l'image.
    """
    if len(image.shape) == 2:
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        return clahe.apply(image)
        
    # Convertir en espace colorimétrique LAB pour travailler sur la luminance (L)
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # Appliquer CLAHE sur le canal de luminance L
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    cl = clahe.apply(l)
    
    # Recombiner et convertir à nouveau en BGR
    limg = cv2.merge((cl, a, b))
    enhanced = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    
    return enhanced

def preprocess_fundus_image(image_path_or_array, target_size=512, sigma=10):
    """
    Pipeline complet de prétraitement clinique pour une image de fond d'œil :
    1. Chargement de l'image (si chemin fourni)
    2. Rognage circulaire de la rétine
    3. Redimensionnement préliminaire
    4. Soustraction de couleur locale de Ben Graham
    5. Amélioration locale des contrastes via CLAHE
    6. Redimensionnement final à la taille cible (512x512)
    """
    # 1. Charger l'image si c'est un chemin
    if isinstance(image_path_or_array, str):
        if not os.path.exists(image_path_or_array):
            raise FileNotFoundError(f"Image introuvable : {image_path_or_array}")
        image = cv2.imread(image_path_or_array)
    else:
        image = image_path_or_array.copy()
        
    if image is None:
        raise ValueError("Impossible de charger ou lire l'image.")
        
    # 2. Rognage de la rétine
    image_cropped = crop_retina_circle(image)
    
    # 3. Redimensionnement intermédiaire rapide pour le filtre de Graham
    # (permet un comportement constant quel que soit la résolution initiale)
    image_resized = cv2.resize(image_cropped, (target_size, target_size))
    
    # 4. Méthode Ben Graham
    image_graham = ben_graham_preprocessing(image_resized, sigma=sigma)
    
    # 5. Égalisation de contraste adaptative CLAHE
    image_preprocessed = apply_clahe(image_graham)
    
    return image_preprocessed

# Code de test rapide pour validation hors ligne
if __name__ == "__main__":
    print("Test du pipeline de prétraitement RetinAI...")
    # Générer une fausse image de fond d'œil (un cercle jaune/orange sur fond noir)
    dummy_img = np.zeros((600, 800, 3), dtype=np.uint8)
    cv2.circle(dummy_img, (400, 300), 200, (20, 100, 220), -1)  # Cercle orangeâtre
    cv2.circle(dummy_img, (430, 280), 10, (150, 200, 255), -1)  # Tache simulant la papille optique
    cv2.circle(dummy_img, (380, 330), 4, (0, 0, 180), -1)       # Petite tache simulant une hémorragie
    
    # Exécuter le pipeline
    try:
        out = preprocess_fundus_image(dummy_img, target_size=512)
        print(f"[OK] Pretraitement reussi ! Image de sortie : {out.shape} (min: {out.min()}, max: {out.max()})")
    except Exception as e:
        print(f"[ERROR] Erreur lors du test : {e}")
