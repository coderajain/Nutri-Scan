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

        # 3. CLAHE Contrast Enhancement (sharpens letters on low-contrast food packaging)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        contrast_enhanced = clahe.apply(gray)

        # 4. Bilateral filter: removes packaging noise/glare while preserving sharp text edges
        denoised = cv2.bilateralFilter(contrast_enhanced, d=7, sigmaColor=50, sigmaSpace=50)

        # 5. Deskewing
        deskewed, angle = cls._deskew(denoised)

        # Ensure destination directory exists safely
        out_dir = os.path.dirname(output_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

        # Save enhanced grayscale image (preserves antialiased font edges for Tesseract LSTM neural net)
        cv2.imwrite(output_path, deskewed)

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
        """Calculates skew angle from text edge contours and rotates the image horizontally."""
        try:
            edges = cv2.Canny(image, 50, 150, apertureSize=3)
            coords = np.column_stack(np.where(edges > 0))
            if coords.shape[0] < 100:
                return image, 0.0

            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = -(90 + angle)
            elif angle > 45:
                angle = -(angle - 90)
            else:
                angle = -angle

            # Only apply subtle rotation correction between 0.5 and 15 degrees
            if abs(angle) < 0.5 or abs(angle) > 15:
                return image, 0.0

            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(
                image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
            )
            return rotated, angle
        except Exception:
            return image, 0.0
