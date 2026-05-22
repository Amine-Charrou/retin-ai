import torch
import argparse
import os
from model import RetinAIModel

def export_to_onnx(model_path, output_path, model_name='efficientnet_b4', image_size=512):
    """
    Exporte un checkpoint PyTorch (.pth) au format ONNX optimisé.
    Ce format permet d'accélérer l'inférence de 2x à 5x sur CPU et GPU
    dans notre serveur de production FastAPI.
    """
    print(f"Initialisation du modèle {model_name}...")
    # 1. Charger l'architecture du modèle
    model = RetinAIModel(model_name=model_name, pretrained=False, num_classes=5)
    
    # 2. Charger les poids entraînés
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Checkpoint PyTorch introuvable sous : {model_path}")
        
    print(f"Chargement des poids depuis {model_path}...")
    device = torch.device("cpu") # L'export ONNX se fait préférentiellement sur CPU
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    
    # 3. Créer un tenseur d'entrée factice respectant la forme attendue [batch, canaux, H, W]
    dummy_input = torch.randn(1, 3, image_size, image_size, requires_grad=False)
    
    # 4. Exporter le modèle vers le format ONNX
    print(f"Début de la sérialisation ONNX (Opset Version 14)...")
    torch.onnx.export(
        model,                              # Le modèle PyTorch
        dummy_input,                        # Entrée factice pour tracer l'exécution
        output_path,                        # Chemin du fichier ONNX de sortie
        export_params=True,                 # Exporter tous les paramètres/poids
        opset_version=14,                   # Version recommandée de l'Opset ONNX
        do_constant_folding=True,           # Optimisation de pliage des constantes
        input_names=['input'],              # Nommage du nœud d'entrée
        output_names=['output'],            # Nommage du nœud de sortie
        dynamic_axes={                      # Rendre le batch dynamique pour le serveur API
            'input': {0: 'batch_size'},
            'output': {0: 'batch_size'}
        }
    )
    
    print(f"✓ Modèle ONNX exporté et sauvegardé avec succès sous : {output_path}")
    print("\nPour charger ce modèle dans votre API de production FastAPI :")
    print("```python")
    print("import onnxruntime as ort")
    print(f"ort_session = ort.InferenceSession('{output_path}')")
    print("outputs = ort_session.run(None, {'input': preprocessed_image_numpy})")
    print("```")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export du modèle RetinAI vers ONNX")
    parser.add_argument('--model_path', type=str, default='best_model_fold_1.pth', help="Chemin du checkpoint PyTorch (.pth)")
    parser.add_argument('--output_path', type=str, default='retinai_model.onnx', help="Nom du fichier ONNX de sortie")
    parser.add_argument('--model_name', type=str, default='efficientnet_b4', help="Nom du backbone")
    parser.add_argument('--image_size', type=int, default=512, help="Taille des images")
    
    try:
        args = parser.parse_args()
        export_to_onnx(args.model_path, args.output_path, args.model_name, args.image_size)
    except Exception as e:
        print(f"Note : Script configuré pour exécution en ligne de commande. Erreur : {e}")
        print("Usage: python export_onnx.py --model_path <path> --output_path <path>")
