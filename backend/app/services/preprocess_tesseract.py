"""Tesseract fallback preprocessing pipeline (morphological table grid removal and margin cropping)."""
import os
import cv2
import numpy as np
import logging

logger = logging.getLogger("nutriscan.services.preprocess_tesseract")


def preprocess_for_tesseract(input_path: str, output_path: str, debug_dir: str = None) -> str:
    """
    Applies dedicated preprocessing for Tesseract on curved and bordered packaging:
    1. Crops out extreme curved left/right 10% margins.
    2. Applies CLAHE contrast enhancement.
    3. Performs Otsu binarization.
    4. Detects and erases horizontal (50, 1) and vertical (1, 50) table grid lines via MORPH_OPEN.
    5. Inverts to black text on white background (cv2.bitwise_not).
    """
    img = cv2.imread(input_path)
    if img is None:
        raise ValueError(f"Could not read image at: {input_path}")

    h, w = img.shape[:2]
    if max(h, w) > 1800:
        scale = 1800.0 / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
        h, w = img.shape[:2]

    # 1. Crop out the extreme curved left/right 10% margins
    x_start = int(0.10 * w)
    x_end = int(0.90 * w)
    cropped = img[:, x_start:x_end]

    # 2. Grayscale & CLAHE
    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # 3. Otsu binarization
    _, otsu = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # If dark text on light background, invert for grid detection so text/lines are white (255)
    mean_val = np.mean(otsu)
    white_fg = otsu if mean_val < 127 else cv2.bitwise_not(otsu)

    # 4. Detect horizontal & vertical grid lines using morphological opening
    h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 1))
    h_lines = cv2.morphologyEx(white_fg, cv2.MORPH_OPEN, h_kernel)

    v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 50))
    v_lines = cv2.morphologyEx(white_fg, cv2.MORPH_OPEN, v_kernel)

    grid = cv2.add(h_lines, v_lines)

    # Erase grid lines from foreground
    no_grid = cv2.subtract(white_fg, grid)

    # 5. Bitwise not so text is black on white background
    final_img = cv2.bitwise_not(no_grid)

    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    cv2.imwrite(output_path, final_img)

    if debug_dir:
        os.makedirs(debug_dir, exist_ok=True)
        cv2.imwrite(os.path.join(debug_dir, "tess_1_cropped.png"), cropped)
        cv2.imwrite(os.path.join(debug_dir, "tess_2_clahe.png"), enhanced)
        cv2.imwrite(os.path.join(debug_dir, "tess_3_otsu.png"), otsu)
        cv2.imwrite(os.path.join(debug_dir, "tess_4_grid.png"), grid)
        cv2.imwrite(os.path.join(debug_dir, "tess_5_no_grid.png"), no_grid)
        cv2.imwrite(os.path.join(debug_dir, "tess_6_final.png"), final_img)

    return output_path
