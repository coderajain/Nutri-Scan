"""OpenCV image preprocessing pipeline for label OCR (SCAN-004, SAF-004)."""
import os
import cv2
import numpy as np
from PIL import Image
import logging

logger = logging.getLogger("nutriscan.services.image_processor")


class ImageProcessor:
    """Preprocesses packaged commodity label photographs to maximize OCR character recognition."""

    @staticmethod
    def validate_image_file(file_path: str) -> bool:
        """Verifies that the file exists and is a valid readable image."""
        if not os.path.exists(file_path):
            return False
        try:
            with Image.open(file_path) as img:
                img.verify()
            return True
        except Exception:
            return False

    @classmethod
    def preprocess_image(cls, input_path: str, output_path: str) -> dict:
        """
        Executes a 5-stage image enhancement pipeline:
        1. Resizing to standard high-DPI resolution while maintaining aspect ratio
        2. Grayscale conversion
        3. CLAHE (Contrast Limited Adaptive Histogram Equalization)
        4. Bilateral filtering for noise reduction with edge preservation
        5. Deskewing / orientation correction
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input image not found: {input_path}")

        # Load image via OpenCV
        img = cv2.imread(input_path)
        if img is None:
            raise ValueError(f"Could not decode image at: {input_path}")

        original_h, original_w = img.shape[:2]
        
        # 1. Resize if image is too small or too large
        target_w = 2000
        if original_w < 1200 or original_w > 3000:
            scale = target_w / float(original_w)
            target_h = int(original_h * scale)
            img_resized = cv2.resize(img, (target_w, target_h), interpolation=cv2.INTER_CUBIC)
        else:
            img_resized = img.copy()

        # 2. Grayscale conversion
        gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)

        # 3. CLAHE Contrast Enhancement
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        contrast_enhanced = clahe.apply(gray)

        # 4. Bilateral filter for noise reduction without blurring text edges
        denoised = cv2.bilateralFilter(contrast_enhanced, d=9, sigmaColor=75, sigmaSpace=75)

        # 5. Deskewing
        deskewed, angle = cls._deskew(denoised)

        # 6. Adaptive Thresholding (Otsu thresholding for crisp text characters)
        _, thresh = cv2.threshold(deskewed, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Ensure destination directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cv2.imwrite(output_path, thresh)

        logger.info(f"Processed image saved to {output_path} (Rotation applied: {angle:.2f}°)")

        return {
            "original_width": original_w,
            "original_height": original_h,
            "processed_width": deskewed.shape[1],
            "processed_height": deskewed.shape[0],
            "deskew_angle": round(angle, 2),
            "processed_image_path": output_path,
        }

    @staticmethod
    def _deskew(image: np.ndarray) -> tuple[np.ndarray, float]:
        """Calculates skew angle and rotates the image horizontally."""
        # Find coordinates of all non-zero pixels
        coords = np.column_stack(np.where(image > 0))
        if coords.shape[0] < 50:
            return image, 0.0

        angle = cv2.minAreaRect(coords)[-1]
        # In OpenCV minAreaRect returns angle in [-90, 0)
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        # If angle is minimal, skip rotation to avoid interpolation artifacts
        if abs(angle) < 0.5 or abs(angle) > 45:
            return image, 0.0

        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
        )
        return rotated, angle
