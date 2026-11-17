"""Tesseract OCR wrapper with confidence and layout metadata extraction (OCR-001, OCR-003)."""
import os
import shutil
import pytesseract
from PIL import Image
import logging

logger = logging.getLogger("nutriscan.services.ocr_engine")


class OCREngine:
    """Invokes Tesseract OCR 5.x on the preprocessed image and extracts raw text + confidence metadata."""

    def __init__(self, tesseract_cmd: str = None):
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        else:
            # Check standard Windows paths if on Windows
            win_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Users\hp\AppData\Local\Programs\Tesseract-OCR\tesseract.exe",
            ]
            for p in win_paths:
                if os.path.exists(p):
                    pytesseract.pytesseract.tesseract_cmd = p
                    break

    @classmethod
    def is_tesseract_available(cls) -> bool:
        """Checks if Tesseract binary is accessible."""
        try:
            return shutil.which("tesseract") is not None or os.path.exists(pytesseract.pytesseract.tesseract_cmd)
        except Exception:
            return False

    def extract_text(self, image_path: str) -> dict:
        """
        Performs OCR text recognition and detailed confidence score analysis.
        Returns:
            {
                "raw_text": str,
                "confidence_avg": float (0-100),
                "words_detected": int,
                "low_confidence_word_count": int,
                "uncertain_flags": list[str]
            }
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found for OCR: {image_path}")

        try:
            image = Image.open(image_path)
            
            # Custom Tesseract configuration for packaged commodity labels:
            # --oem 1: LSTM Neural Net OCR Engine
            # --psm 3: Fully automatic page segmentation without OSD
            custom_config = r"--oem 1 --psm 3"

            # 1. Full string extraction
            raw_text = pytesseract.image_to_string(image, config=custom_config)

            # 2. Detailed word-level confidence extraction
            data = pytesseract.image_to_data(image, config=custom_config, output_type=pytesseract.Output.DICT)
            
            confidences = []
            low_conf_words = []
            
            for i, word in enumerate(data.get("text", [])):
                word = word.strip()
                if not word:
                    continue
                try:
                    conf = float(data["conf"][i])
                    if conf > 0:  # -1 represents blocks/paragraphs without confidence
                        confidences.append(conf)
                        if conf < 60.0 and len(word) > 2:
                            low_conf_words.append(word)
                except (ValueError, TypeError):
                    continue

            avg_conf = float(sum(confidences) / len(confidences)) if confidences else 0.0

            uncertainty_flags = []
            if avg_conf < 65.0 and len(raw_text.strip()) > 0:
                uncertainty_flags.append(f"Low overall OCR confidence ({avg_conf:.1f}%). Findings should be manually reviewed.")

            return {
                "raw_text": raw_text.strip(),
                "confidence_avg": round(avg_conf, 2),
                "words_detected": len(confidences),
                "low_confidence_word_count": len(low_conf_words),
                "uncertain_flags": uncertainty_flags,
            }

        except Exception as exc:
            logger.error(f"Tesseract OCR failed: {exc}")
            # If Tesseract binary is not installed in the current environment, provide a fallback message
            return {
                "raw_text": "",
                "confidence_avg": 0.0,
                "words_detected": 0,
                "low_confidence_word_count": 0,
                "uncertain_flags": [f"OCR execution error: {str(exc)}"],
            }
