import torch
import torch.nn as nn
import torch.nn.functional as F

class OrdinalTargetEncoder:
    """
    Encodeur/Décodeur pour la régression ordinale.
    Convertit un stade entier (0 à 4) en un vecteur binaire cumulatif de taille 4.
    
    Exemples d'encodage :
    - Stade 0 -> [0, 0, 0, 0]
    - Stade 1 -> [1, 0, 0, 0]
    - Stade 2 -> [1, 1, 0, 0]
    - Stade 3 -> [1, 1, 1, 0]
    - Stade 4 -> [1, 1, 1, 1]
    """
    @staticmethod
    def encode(labels, num_classes=5, device=None):
        """
        Convertit un tenseur de labels [batch_size] en tenseur cumulatif [batch_size, num_classes-1].
        """
        batch_size = labels.size(0)
        num_tasks = num_classes - 1
        
        # Créer une matrice de zéros
        encoded = torch.zeros((batch_size, num_tasks), dtype=torch.float32, device=device)
        
        # Remplir de 1 les tâches inférieures ou égales au label
        for i in range(batch_size):
            label = labels[i].item()
            if label > 0:
                encoded[i, :label] = 1.0
                
        return encoded

    @staticmethod
    def decode(logits, threshold=0.5):
        """
        Convertit les sorties du modèle (logits non activés de taille [batch_size, 4])
        en prédictions de classes entières (0 à 4).
        
        Méthode : on applique la sigmoïde sur chaque tâche, puis on compte combien
        dépassent le seuil (0.5).
        """
        probs = torch.sigmoid(logits)
        predictions = (probs > threshold).sum(dim=1)
        return predictions

class BinaryFocalLoss(nn.Module):
    """
    Implémentation de la Focal Loss pour la classification binaire.
    Utile pour surmonter le déséquilibre extrême des classes en pénalisant moins
    les exemples faciles (déjà classés avec succès) et en focalisant sur les exemples difficiles.
    
    Formule : Loss = -alpha * (1 - p)^gamma * y * log(p) - (1 - alpha) * p^gamma * (1 - y) * log(1 - p)
    """
    def __init__(self, alpha=0.25, gamma=2.0, reduction='mean'):
        super(BinaryFocalLoss, self).__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.reduction = reduction

    def forward(self, inputs, targets):
        # inputs: logits bruts (non activés par sigmoïde)
        # targets: labels binaires (0 ou 1)
        
        # Calculer la Binary Cross Entropy avec logits stable
        bce_loss = F.binary_cross_entropy_with_logits(inputs, targets, reduction='none')
        
        # Calculer la probabilité p de la classe correcte
        p = torch.sigmoid(inputs)
        p_t = p * targets + (1 - p) * (1 - targets)
        
        # Facteur de focalisation
        focal_weight = (1.0 - p_t) ** self.gamma
        
        # Appliquer alpha pour l'équilibrage des classes
        alpha_t = self.alpha * targets + (1 - self.alpha) * (1 - targets)
        
        loss = alpha_t * focal_weight * bce_loss
        
        if self.reduction == 'mean':
            return loss.mean()
        elif self.reduction == 'sum':
            return loss.sum()
        else:
            return loss

class OrdinalFocalLoss(nn.Module):
    """
    Perte globale d'entraînement pour RetinAI.
    Calcule la Focal Loss binaire sur chacune des 4 sous-tâches de classification cumulée.
    """
    def __init__(self, num_classes=5, alpha=0.25, gamma=2.0):
        super(OrdinalFocalLoss, self).__init__()
        self.num_classes = num_classes
        self.binary_focal = BinaryFocalLoss(alpha=alpha, gamma=gamma, reduction='mean')

    def forward(self, logits, targets):
        """
        Args:
            logits (torch.Tensor): Logits bruts du modèle de forme [batch_size, num_classes-1]
            targets (torch.Tensor): Tenseur de labels réels [batch_size] de valeurs (0 à 4)
        """
        # 1. Encoder les labels entiers en cibles binaires cumulatives
        encoded_targets = OrdinalTargetEncoder.encode(
            targets, 
            num_classes=self.num_classes, 
            device=logits.device
        )
        
        loss = 0.0
        num_tasks = self.num_classes - 1
        
        # 2. Sommer la Focal Loss sur chaque tâche
        for i in range(num_tasks):
            task_logits = logits[:, i]
            task_targets = encoded_targets[:, i]
            loss += self.binary_focal(task_logits, task_targets)
            
        # Diviser par le nombre de tâches pour avoir une moyenne stable
        return loss / num_tasks

# Test unitaire rapide
if __name__ == "__main__":
    print("Test de la Perte Ordinale & Focal Loss...")
    dummy_logits = torch.tensor([
        [2.0, 1.5, -0.5, -3.0],  # Devrait donner Stade 2 (sigmoïdes: [0.88, 0.82, 0.38, 0.05] -> 2 dépassent 0.5)
        [-1.0, -2.0, -3.0, -4.0]  # Devrait donner Stade 0
    ], dtype=torch.float32)
    
    dummy_labels = torch.tensor([2, 0], dtype=torch.long)
    
    # 1. Tester le décodage
    preds = OrdinalTargetEncoder.decode(dummy_logits)
    print(f"[OK] Decodage reussi. Predictions obtenues : {preds.tolist()} (Attendu: [2, 0])")
    
    # 2. Tester l'encodage
    encoded = OrdinalTargetEncoder.encode(dummy_labels)
    print(f"[OK] Encodage reussi. Vecteurs : \n{encoded.tolist()}")
    
    # 3. Tester la fonction de perte
    criterion = OrdinalFocalLoss()
    loss_val = criterion(dummy_logits, dummy_labels)
    print(f"[OK] Calcul de la perte reussi ! Valeur de perte : {loss_val.item():.4f}")
