# Guide d'Entraînement RetinAI sur Kaggle (Gratuit & Rapide)

Ce guide vous explique pas à pas comment exécuter l'entraînement complet de votre modèle **RetinAI** en utilisant les processeurs graphiques (GPU) gratuits de **Kaggle**.

---

## 🛠️ Étape 1 : Préparation de votre compte Kaggle
1. Rendez-vous sur [Kaggle](https://www.kaggle.com/) et créez un compte (ou connectez-vous).
2. **IMPORTANT** : Allez dans vos paramètres de profil (`Settings`), faites défiler jusqu'à la section **Phone Verification** et faites vérifier votre numéro de téléphone. 
   * *Pourquoi ?* Cela débloque l'accès aux **GPU gratuits (30 heures par semaine)** et vous permet d'activer la connexion Internet dans vos notebooks (nécessaire pour télécharger `timm` et vous connecter à `Weights & Biases`).

---

## 📂 Étape 2 : Créer un nouveau Notebook et ajouter les Datasets
1. Cliquez sur le bouton **"+"** en haut à gauche de la page d'accueil de Kaggle, puis sélectionnez **New Notebook**.
2. Dans le menu de droite du notebook, sous la section **Settings** :
   * Réglez **Accelerator** sur **GPU T4 x2** (ou GPU T4 simple).
   * Activez l'option **Internet on** (sélectionnez l'interrupteur).
3. Cliquez sur **"+ Add Input"** (ou *Add Data*) en haut à droite pour lier les jeux de données :
   * Recherchez **"Aptos 2019"** et cliquez sur le bouton "+" pour ajouter le dataset **APTOS 2019 Blindness Detection** (qui contient les images de fond d'œil annotées de 0 à 4).
   * Si vous voulez plus de données, recherchez **"Diabetic Retinopathy Detection"** (EyePACS) pour l'ajouter également.

---

## 📤 Étape 3 : Importer vos scripts de code dans Kaggle
Vous avez deux options pour charger les fichiers que nous avons créés (`preprocess.py`, `dataset.py`, `model.py`, `loss.py`, `train.py`) dans Kaggle :

### Option A (La plus propre - Téléverser les fichiers)
1. Dans le panneau de droite de Kaggle, cliquez sur le bouton de téléversement (icône flèche vers le haut) à côté de la section **Files**.
2. Sélectionnez tous les scripts Python de votre dossier local `projetIA_indus/training/` et importez-les. Ils apparaîtront dans le dossier `/kaggle/working/`.

### Option B (Copier-coller rapide dans des cellules)
Créez une cellule de code pour chaque script et utilisez la commande magique `%%writefile` en première ligne pour écrire le fichier directement sur Kaggle. 

Exemple de cellule Kaggle :
```python
%%writefile preprocess.py
# Copiez ici l'intégralité du code de preprocess.py...
```
Exécutez la cellule, et Kaggle créera automatiquement le fichier `preprocess.py` dans son espace de travail. Répétez pour chaque fichier.

---

## ⚡ Étape 4 : Installer les dépendances
Dans la première cellule de votre notebook, installez les dépendances complémentaires nécessaires (elles ne sont pas toutes installées par défaut sur Kaggle) :

```python
!pip install -q timm albumentations wandb mlflow onnx onnxruntime
```

---

## 🏃‍♂️ Étape 5 : Lancer l'entraînement
Dans une nouvelle cellule, lancez l'entraînement à 5-Fold avec vos paramètres en utilisant le dataset APTOS 2019 :

```python
!python train.py \
  --csv_path /kaggle/input/aptos2019-blindness-detection/train.csv \
  --img_dir /kaggle/input/aptos2019-blindness-detection/train_images \
  --model_name efficientnet_b4 \
  --epochs 15 \
  --batch_size 16 \
  --lr 3e-4 \
  --pretrained \
  --use_wandb
```

### 💡 Conseils pour l'entraînement :
* **Suivi en direct** : Pendant l'entraînement, le script vous demandera une clé **Weights & Biases**. Copiez-collez votre clé d'API wandb (que vous trouverez gratuitement sur votre profil wandb.ai) directement dans l'invite de commande Kaggle. Vous pourrez voir les magnifiques courbes d'entraînement QWK et Focal Loss se tracer en temps réel depuis votre smartphone ou un autre onglet !
* **Batch size** : Le GPU T4 de Kaggle possède 16 Go de VRAM, ce qui permet d'utiliser un `--batch_size` plus grand (16 ou 32) pour accélérer considérablement l'apprentissage.

---

## 💾 Étape 6 : Récupérer votre modèle final ONNX
Une fois les folds terminés, exportez le meilleur fold au format ONNX :

```python
!python export_onnx.py --model_path best_model_fold_1.pth --output_path retinai_model.onnx
```

1. Dans le panneau de droite de Kaggle, actualisez le dossier de sortie `/kaggle/working/`.
2. Repérez le fichier `retinai_model.onnx` nouvellement généré.
3. Cliquez sur les trois petits points à côté du nom du fichier et sélectionnez **Download**.
4. Déplacez ce fichier sur votre PC local dans le dossier de votre projet ! Vous avez maintenant un modèle de Deep Learning professionnel, ultra-léger et optimisé pour alimenter votre API FastAPI en production ! 🎉
