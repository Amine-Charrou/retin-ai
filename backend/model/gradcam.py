"""
RetinAI — Grad-CAM–style Heatmap Generator (ONNX-compatible)

Since ONNX Runtime doesn't support gradient computation, this module generates
a synthetic activation heatmap by analysing the green-channel intensity of the
retinal image. For stages > 0, high-intensity vascular regions are highlighted
with a JET colormap overlay. For stage 0 (healthy), a cool/neutral overlay is
returned.
"""
import cv2
import numpy as np
from pathlib import Path


def generate_heatmap(image_path: str, output_path: str, stage: int = 0) -> str:
    """
    Generate a Grad-CAM–style heatmap overlay for a retinal fundus image.

    Args:
        image_path: Path to the original fundus image.
        output_path: Path where the heatmap image will be saved.
        stage: Predicted DR stage (0-4). Controls overlay intensity.

    Returns:
        The output_path string.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Could not read image: {image_path}")

    h, w = img.shape[:2]

    # ── Create a circular mask (fundus images are typically circular) ─────
    center = (w // 2, h // 2)
    radius = int(min(h, w) * 0.45)
    circle_mask = np.zeros((h, w), dtype=np.uint8)
    cv2.circle(circle_mask, center, radius, 255, -1)

    # ── Extract green channel (best contrast for retinal vessels) ─────────
    green = img[:, :, 1].astype(np.float32)

    # Apply CLAHE to enhance vascular structures
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(green.astype(np.uint8))

    # Invert so that dark vessels become bright hotspots
    inverted = 255 - enhanced

    # Gaussian blur to create smooth activation blobs
    blur_size = max(h, w) // 6
    if blur_size % 2 == 0:
        blur_size += 1
    activation = cv2.GaussianBlur(inverted.astype(np.float32), (blur_size, blur_size), 0)

    # Normalize to 0-255
    activation = cv2.normalize(activation, None, 0, 255, cv2.NORM_MINMAX)

    # Apply circle mask
    activation = cv2.bitwise_and(activation.astype(np.uint8), circle_mask)

    # ── Adjust intensity based on stage ──────────────────────────────────
    if stage == 0:
        # Very subtle overlay for healthy retinas
        activation = (activation * 0.15).astype(np.uint8)
    elif stage == 1:
        activation = (activation * 0.4).astype(np.uint8)
    elif stage == 2:
        activation = (activation * 0.6).astype(np.uint8)
    elif stage == 3:
        activation = (activation * 0.8).astype(np.uint8)
    else:  # stage 4
        activation = (activation * 1.0).astype(np.uint8)

    # ── Apply JET colormap ───────────────────────────────────────────────
    heatmap_colored = cv2.applyColorMap(activation, cv2.COLORMAP_JET)

    # ── Blend with original image ────────────────────────────────────────
    alpha = 0.45  # heatmap opacity
    overlay = cv2.addWeighted(img, 1 - alpha, heatmap_colored, alpha, 0)

    # Restore non-fundus area to black
    mask_3c = cv2.merge([circle_mask, circle_mask, circle_mask])
    outside = np.where(mask_3c == 0)
    overlay[outside] = 0

    # Save result
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(output_path, overlay)

    return output_path
