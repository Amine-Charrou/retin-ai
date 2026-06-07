import onnxruntime as ort
import numpy as np
from PIL import Image
import sys

# ── Config ────────────────────────────────────────────────────────────────────
CLASS_NAMES = ["No DR", "Mild", "Moderate", "Severe", "Proliferative"]
MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32).reshape(3, 1, 1)
STD  = np.array([0.229, 0.224, 0.225], dtype=np.float32).reshape(3, 1, 1)

def transform(img):
    """Resize, to-tensor, normalize — pure PIL + numpy, no torch needed."""
    img = img.resize((224, 224), Image.BILINEAR)
    arr = np.array(img, dtype=np.float32) / 255.0   # HWC, 0-1
    arr = arr.transpose(2, 0, 1)                     # CHW
    arr = (arr - MEAN) / STD
    return arr[np.newaxis, ...]                       # add batch dim

# ── Load model ────────────────────────────────────────────────────────────────
import os
MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
session = ort.InferenceSession(os.path.join(MODEL_DIR, "dr_model_v2.onnx"))
print("[OK] Model loaded")

# ── Predict (API) ─────────────────────────────────────────────────────────────
def predict_from_pil(image_path: str) -> dict:
    """
    Run inference on an image and return structured results.
    Used by the FastAPI backend.
    """
    img = Image.open(image_path).convert("RGB")
    img_t = transform(img)

    logits = session.run(["logits"], {"image": img_t})[0]
    probs = np.exp(logits) / np.exp(logits).sum()
    pred = int(probs[0].argmax())

    return {
        "stage": pred,
        "class_name": CLASS_NAMES[pred],
        "confidence": float(probs[0][pred]),
        "probabilities": [float(p) for p in probs[0]]
    }


# ── Predict (CLI) ─────────────────────────────────────────────────────────────
def predict(image_path):
    img    = Image.open(image_path).convert("RGB")
    img_t  = transform(img)

    logits = session.run(["logits"], {"image": img_t})[0]
    probs  = np.exp(logits) / np.exp(logits).sum()
    pred   = probs[0].argmax()

    print("\n" + "=" * 45)
    print(f"  Image      : {image_path}")
    print(f"  Prediction : Grade {pred} - {CLASS_NAMES[pred]}")
    print(f"  Confidence : {probs[0][pred]*100:.1f}%")
    print("=" * 45)
    print("\nAll probabilities:")
    for i, (name, prob) in enumerate(zip(CLASS_NAMES, probs[0])):
        bar = "#" * int(prob * 30)
        marker = " <--" if i == pred else ""
        print(f"  Grade {i} {name:>13s} : {prob*100:5.1f}%  {bar}{marker}")

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python predict.py <image_path>")
        print("Example: python predict.py test_grade2.png")
    else:
        predict(sys.argv[1])