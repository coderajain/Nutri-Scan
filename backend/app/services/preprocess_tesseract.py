"""Tesseract fallback preprocessing pipeline (contrast normalization and shadow compensation)."""
import os
import cv2
import numpy as np
import logging

logger = logging.getLogger("nutriscan.services.preprocess_tesseract")


def preprocess_for_tesseract(input_path: str, output_path: str, debug_dir: str = None) -> str:
    """
    Applies non-destructive preprocessing for Tesseract OCR on packaging labels:
    1. Scales image to optimal dimension (max 2200px) preserving aspect ratio.
    2. Converts to grayscale.
    3. Normalizes uneven lighting and curved container shadows via background division.
    4. Applies CLAHE contrast enhancement for sharp character edges.
    5. Preserves full image margins and stroke geometry (no destructive line subtraction).
    """
    img = cv2.imread(input_path)
    if img is None:
        raise ValueError(f"Could not read image at: {input_path}")

    h, w = img.shape[:2]
    if max(h, w) > 2200:
        scale = 2200.0 / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 1. Background division for shadow and curvature gradient compensation
    bg = cv2.GaussianBlur(gray, (51, 51), 0)
    bg[bg == 0] = 1
    norm = cv2.divide(gray, bg, scale=255)

    # 2. CLAHE contrast enhancement
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(norm)

    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    cv2.imwrite(output_path, enhanced)

    if debug_dir:
        os.makedirs(debug_dir, exist_ok=True)
        cv2.imwrite(os.path.join(debug_dir, "tess_enhanced.png"), enhanced)

    return output_path
