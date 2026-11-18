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
        1.5x bicubic upscale + light CLAHE on L-channel (LAB space) for deep-learning detector.
        """
        img = cv2.imread(input_path)
        if img is None:
            raise ValueError(f"Could not decode image at: {input_path}")

        # 1. Upscale 1.5x bicubic
        resized = cv2.resize(img, (0, 0), fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)

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
