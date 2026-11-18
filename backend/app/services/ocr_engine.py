"""Tesseract OCR wrapper with multi-pass recognition and confidence extraction (OCR-001, OCR-003)."""
import os
import shutil
import pytesseract
from PIL import Image
from typing import Optional
from app.core.config import settings
import logging

logger = logging.getLogger("nutriscan.services.ocr_engine")

# Determine and register Tesseract executable path
_POSSIBLE_PATHS = [
    getattr(settings, "TESSERACT_CMD", None),
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    r"C:\Users\hp\AppData\Local\Programs\Tesseract-OCR\tesseract.exe",
]

_configured_cmd = None
for p in _POSSIBLE_PATHS:
    if p and os.path.exists(p):
        _configured_cmd = p
        break

if _configured_cmd:
    pytesseract.pytesseract.tesseract_cmd = _configured_cmd
    tess_dir = os.path.dirname(_configured_cmd)
    if tess_dir and tess_dir not in os.environ.get("PATH", ""):
        os.environ["PATH"] = f"{tess_dir};" + os.environ.get("PATH", "")
    logger.info(f"Tesseract OCR registered at: {_configured_cmd}")


class OCREngine:
    """Invokes Tesseract OCR 5.x on preprocessed and raw images using multi-pass recognition."""

    def __init__(self, tesseract_cmd: Optional[str] = None):
        if tesseract_cmd and os.path.exists(tesseract_cmd):
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        elif _configured_cmd:
            pytesseract.pytesseract.tesseract_cmd = _configured_cmd

    @classmethod
    def is_tesseract_available(cls) -> bool:
        """Checks if Tesseract binary is accessible."""
        try:
            cmd = getattr(pytesseract.pytesseract, "tesseract_cmd", "tesseract")
            return (bool(cmd) and os.path.exists(cmd)) or (shutil.which("tesseract") is not None)
        except Exception:
            return False

    def extract_text(self, image_path: str, raw_image_path: Optional[str] = None) -> dict:
        """
        Performs multi-pass OCR text recognition across sparse and block segmentation modes.
        Combines detections from enhanced and original image passes to maximize character recovery.
        
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

        # Ensure tesseract path is active
        if _configured_cmd and not os.path.exists(getattr(pytesseract.pytesseract, "tesseract_cmd", "")):
            pytesseract.pytesseract.tesseract_cmd = _configured_cmd

        paths_to_scan = [image_path]
        if raw_image_path and os.path.exists(raw_image_path) and raw_image_path != image_path:
            paths_to_scan.append(raw_image_path)

        all_lines: list[str] = []
        confidences: list[float] = []
        low_conf_words: list[str] = []

        # PSM modes:
        # 11: Sparse text. Finds as much text as possible in no particular order (great for food labels)
        # 6: Assume a single uniform block of text (great for nutrition tables and ingredients)
        psm_configs = [
            r"--oem 1 --psm 11",
            r"--oem 1 --psm 6",
        ]

        for path in paths_to_scan:
            try:
                with Image.open(path) as img:
                    for cfg in psm_configs:
                        try:
                            # 1. Text extraction
                            txt = pytesseract.image_to_string(img, config=cfg)
                            for line in txt.splitlines():
                                clean_l = line.strip()
                                if len(clean_l) >= 2 and clean_l not in all_lines:
                                    all_lines.append(clean_l)

                            # 2. Confidence analysis on primary pass
                            if not confidences:
                                data = pytesseract.image_to_data(img, config=cfg, output_type=pytesseract.Output.DICT)
                                for i, word in enumerate(data.get("text", [])):
                                    w = word.strip()
                                    if not w:
                                        continue
                                    try:
                                        c = float(data["conf"][i])
                                        if c > 0:
                                            confidences.append(c)
                                            if c < 60.0 and len(w) > 2:
                                                low_conf_words.append(w)
                                    except (ValueError, TypeError):
                                        continue
                        except Exception as pass_err:
                            logger.debug(f"OCR pass with config {cfg} on {path} returned: {pass_err}")
            except Exception as file_err:
                logger.error(f"Failed to open image {path} for OCR: {file_err}")

        # Compute summary metrics
        raw_text = "\n".join(all_lines).strip()
        avg_conf = float(sum(confidences) / len(confidences)) if confidences else (75.0 if len(all_lines) > 5 else 0.0)

        uncertainty_flags = []
        if avg_conf < 60.0 and len(raw_text) > 0:
            uncertainty_flags.append(f"Low overall OCR confidence ({avg_conf:.1f}%). Findings should be manually reviewed.")
        elif not raw_text:
            uncertainty_flags.append("No readable text recognized by OCR on label image. Please ensure packaging is well-lit and in focus.")

        logger.info(f"Multi-pass OCR complete: {len(all_lines)} lines, {len(confidences)} words, avg conf {avg_conf:.1f}%")

        return {
            "raw_text": raw_text,
            "confidence_avg": round(avg_conf, 2),
            "words_detected": len(confidences) if confidences else len(raw_text.split()),
            "low_confidence_word_count": len(low_conf_words),
            "uncertain_flags": uncertainty_flags,
        }
