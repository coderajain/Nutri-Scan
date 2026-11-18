"""Image preprocessing pipeline for PaddleOCR and Tesseract fallback."""
import os
import cv2
import numpy as np
from PIL import Image
import logging
from app.services.preprocess_tesseract import preprocess_for_tesseract

logger = logging.getLogger("nutriscan.services.image_processor")


class ImageProcessor:
    """Preprocesses packaged commodity label photographs for PaddleOCR and Tesseract."""

    @staticmethod
    def validate_image_file(file_path: str) -> bool:
        if not os.path.exists(file_path):
            return False
        try:
            with Image.open(file_path) as img:
                img.verify()
            return True
        except Exception:
            return False

    @classmethod
    def preprocess_for_paddle(cls, input_path: str, output_path: str) -> str:
        """
        Smart-scales image to optimal OCR resolution (1400-1800px max dimension)
        and applies light CLAHE on L-channel (LAB space) for deep-learning detector.
        Prevents excessive memory usage and CPU stalls from oversized phone photos.
        """
        img = cv2.imread(input_path)
        if img is None:
            raise ValueError(f"Could not decode image at: {input_path}")

        h, w = img.shape[:2]
        max_dim = max(h, w)

        # 1. Optimal resolution scaling for fast, accurate CPU OCR
        if max_dim < 1100:
            # Low resolution: upscale up to 1.5x for clarity
            scale = min(1.5, 1500.0 / max_dim)
            resized = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_CUBIC)
        elif max_dim > 1800:
            # High-resolution phone camera photo (e.g. 12-48 MP): downscale to 1800px max
            # This drastically accelerates inference (from ~20s down to ~2-3s) without text loss
            scale = 1800.0 / max_dim
            resized = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
        else:
            resized = img

        # 2. Light CLAHE on L-channel (LAB color space)
        lab = cv2.cvtColor(resized, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l_clahe = clahe.apply(l)
        enhanced = cv2.cvtColor(cv2.merge((l_clahe, a, b)), cv2.COLOR_LAB2BGR)

        out_dir = os.path.dirname(output_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        cv2.imwrite(output_path, enhanced)
        return output_path

    @classmethod
    def preprocess_image(cls, input_path: str, output_path: str) -> dict:
        """
        Default preprocessor for NutriScan pipeline:
        Produces PaddleOCR-ready enhanced image.
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input image not found: {input_path}")

        img = cv2.imread(input_path)
        if img is None:
            raise ValueError(f"Could not decode image at: {input_path}")

        orig_h, orig_w = img.shape[:2]
        proc_path = cls.preprocess_for_paddle(input_path, output_path)
        proc_img = cv2.imread(proc_path)
        p_h, p_w = proc_img.shape[:2] if proc_img is not None else (orig_h, orig_w)

        return {
            "original_width": orig_w,
            "original_height": orig_h,
            "processed_width": p_w,
            "processed_height": p_h,
            "deskew_angle": 0.0,
            "processed_image_path": proc_path,
        }
