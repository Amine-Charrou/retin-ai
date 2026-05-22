import torch
import torch.nn as nn
import timm

class RetinAIModel(nn.Module):
    """
    Modèle d'apprentissage profond pour RetinAI.
    Utilise un backbone EfficientNet-B4 pré-entraîné de pointe (SOTA)
    adapté pour sortir 4 logits binaires cumulatifs (Régression Ordinale).
    """
    def __init__(self, model_name='efficientnet_b4', pretrained=True, num_classes=5):
        super(RetinAIModel, self).__init__()
        self.model_name = model_name
        self.num_classes = num_classes
        
        # 1. Charger le backbone pré-entraîné via la bibliothèque timm
        # (num_classes=0 supprime le classifieur final d'origine et renvoie directement les features)
        print(f"Chargement du modèle de base {model_name} (pre-trained: {pretrained})...")
        self.backbone = timm.create_model(model_name, pretrained=pretrained, num_classes=0)
        
        # 2. Obtenir le nombre exact de caractéristiques (features) de sortie du backbone
        # timm fournit l'attribut .num_features de façon uniforme pour tous ses modèles
        in_features = self.backbone.num_features
        print(f"Extraction des caractéristiques : {in_features} dimensions.")
        
        # 3. Ajouter une tête de classification personnalisée pour la régression ordinale
        # Le nombre de sorties est égal à (num_classes - 1), soit 4 tâches binaires pour 5 classes
        self.classifier = nn.Sequential(
            nn.Dropout(p=0.4),  # Dropout élevé pour limiter le surapprentissage sur les petits datasets
            nn.Linear(in_features, num_classes - 1)
        )

    def forward(self, x):
        """
        Calcul de propagation avant :
        Reçoit un tenseur d'image [batch_size, 3, 512, 512]
        Retourne les logits de régression ordinale de taille [batch_size, 4]
        """
        # Extraire les caractéristiques spatiales globales (Global Average Pooling inclus par défaut dans timm num_classes=0)
        features = self.backbone(x)
        
        # Passer dans la tête de classification
        logits = self.classifier(features)
        
        return logits

# Test de forme (Shape Test) hors ligne
if __name__ == "__main__":
    print("Test de la structure du modèle RetinAI...")
    try:
        # Créer le modèle sans charger les poids pré-entraînés pour le test de forme
        # afin de ne pas télécharger des centaines de Mo en local
        model = RetinAIModel(model_name='efficientnet_b4', pretrained=False)
        
        # Simuler un batch de 2 images de taille 512x512
        dummy_input = torch.randn(2, 3, 512, 512)
        
        # Propagation avant
        logits = model(dummy_input)
        
        print(f"[OK] Instanciation et forward réussis !")
        print(f"[OK] Forme du tenseur d'entrée : {dummy_input.shape}")
        print(f"[OK] Forme du tenseur de sortie : {logits.shape} (Attendu: [2, 4])")
    except Exception as e:
        print(f"[ERROR] Échec lors du test du modèle : {e}")
