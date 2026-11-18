"""OCR Engine: PaddleOCR (primary deep-learning engine) with Tesseract Fallback."""
import os
import shutil
import cv2
import numpy as np
from PIL import Image
from typing import Optional
from app.core.config import settings
from app.services.preprocess_tesseract import preprocess_for_tesseract
import logging

logger = logging.getLogger("nutriscan.services.ocr_engine")

# Safe environment flags for PaddleX / PaddleOCR CPU execution on Windows
os.environ["PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT"] = "0"
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"

# Register Tesseract fallback executable
_POSSIBLE_PATHS = [
    getattr(settings, "TESSERACT_CMD", None),
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    r"C:\Users\hp\AppData\Local\Programs\Tesseract-OCR\tesseract.exe",
]

_tesseract_cmd = None
for p in _POSSIBLE_PATHS:
    if p and os.path.exists(p):
        _tesseract_cmd = p
        break

if _tesseract_cmd:
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = _tesseract_cmd
    tess_dir = os.path.dirname(_tesseract_cmd)
    if tess_dir and tess_dir not in os.environ.get("PATH", ""):
        os.environ["PATH"] = f"{tess_dir};" + os.environ.get("PATH", "")
    logger.info(f"Tesseract OCR registered at: {_tesseract_cmd}")


_paddle_instance = None

def get_paddle_ocr():
    """Singleton accessor for PaddleOCR engine."""
    global _paddle_instance
    if _paddle_instance is None:
        try:
            from paddleocr import PaddleOCR
            _paddle_instance = PaddleOCR(use_textline_orientation=True, lang="en")
            logger.info("PaddleOCR engine initialized successfully.")
        except Exception as e:
            logger.warning(f"PaddleOCR initialization failed: {e}. Falling back to Tesseract.")
            _paddle_instance = False
    return _paddle_instance if _paddle_instance is not False else None


class OCREngine:
    """Primary PaddleOCR engine with vertical box-grouping and Tesseract fallback."""

    def __init__(self, tesseract_cmd: Optional[str] = None):
        if tesseract_cmd and os.path.exists(tesseract_cmd):
            import pytesseract
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    @classmethod
    def is_tesseract_available(cls) -> bool:
        try:
            import pytesseract
            cmd = getattr(pytesseract.pytesseract, "tesseract_cmd", "tesseract")
            return (bool(cmd) and os.path.exists(cmd)) or (shutil.which("tesseract") is not None)
        except Exception:
            return False

    @staticmethod
    def group_boxes_into_rows(boxes, texts, scores) -> tuple[list[str], list[float]]:
        """
        Groups OCR bounding boxes by vertical Y-coordinate into clean rows.
        Sorts boxes within each row left-to-right so nutrition labels align with numbers.
        """
        if boxes is None or len(boxes) == 0:
            return [t.strip() for t in texts if t.strip()], [float(s) for s in scores]

        items = []
        for b, t, s in zip(boxes, texts, scores):
            t_clean = t.strip()
            if not t_clean:
                continue
            xmin, ymin, xmax, ymax = int(b[0]), int(b[1]), int(b[2]), int(b[3])
            y_center = (ymin + ymax) / 2.0
            h = max(1, ymax - ymin)
            items.append({
                "box": (xmin, ymin, xmax, ymax),
                "text": t_clean,
                "score": float(s),
                "xmin": xmin,
                "xmax": xmax,
                "ymin": ymin,
                "ymax": ymax,
                "y_center": y_center,
                "h": h,
            })

        # Sort top-to-bottom by vertical coordinate
        items.sort(key=lambda x: (x["ymin"], x["xmin"]))

        rows = []
        for item in items:
            matched_row = None
            for r in rows:
                r_ymin = min(x["ymin"] for x in r)
                r_ymax = max(x["ymax"] for x in r)
                r_yc = sum(x["y_center"] for x in r) / len(r)
                r_h = sum(x["h"] for x in r) / len(r)

                y_diff = abs(item["y_center"] - r_yc)
                vertical_overlap = max(0, min(item["ymax"], r_ymax) - max(item["ymin"], r_ymin))

                if vertical_overlap > 0.4 * min(item["h"], r_h) or y_diff <= 0.45 * r_h or abs(item["ymin"] - r_ymin) <= 22:
                    horizontal_overlap = any(
                        max(0, min(item["xmax"], x["xmax"]) - max(item["xmin"], x["xmin"])) > 0.5 * min(item["xmax"] - item["xmin"], x["xmax"] - x["xmin"])
                        for x in r
                    )
                    if not horizontal_overlap:
                        matched_row = r
                        break

            if matched_row is not None:
                matched_row.append(item)
            else:
                rows.append([item])

        rows.sort(key=lambda r: sum(x["y_center"] for x in r) / len(r))

        formatted_lines = []
        confidences = []
        for r in rows:
            r.sort(key=lambda x: x["xmin"])
            line_str = " | ".join(x["text"] for x in r)
            formatted_lines.append(line_str)
            confidences.extend(x["score"] * 100.0 for x in r)

        return formatted_lines, confidences

    def extract_text(self, image_path: str, raw_image_path: Optional[str] = None) -> dict:
        """
        Processes a SINGLE cleaned image per face to prevent 3x text repetition.
        Primary: PaddleOCR with 1.5x bicubic & CLAHE.
        Fallback: Tesseract with grid-erasure on failure.
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found for OCR: {image_path}")

        paddle = get_paddle_ocr()
        lines: list[str] = []
        confidences: list[float] = []

        # 1. Primary Engine: PaddleOCR
        if paddle:
            try:
                img = cv2.imread(image_path)
                if img is not None:
                    preds = paddle.predict(img)
                    for r in preds:
                        boxes = r.get("rec_boxes", [])
                        texts = r.get("rec_texts", [])
                        scores = r.get("rec_scores", [])
                        if len(texts) > 0:
                            row_lines, row_confs = self.group_boxes_into_rows(boxes, texts, scores)
                            lines.extend(row_lines)
                            confidences.extend(row_confs)
            except Exception as e:
                logger.warning(f"PaddleOCR execution error: {e}. Falling back to Tesseract.")

        # 2. Fallback Engine: Tesseract with table grid-line erasure
        if not lines and self.is_tesseract_available():
            try:
                import pytesseract
                tess_tmp = image_path + "_tess_prep.png"
                preprocess_for_tesseract(image_path, tess_tmp)
                with Image.open(tess_tmp) as t_img:
                    txt = pytesseract.image_to_string(t_img, config=r"--oem 1 --psm 6 -l eng")
                    for l in txt.splitlines():
                        c = l.strip()
                        if len(c) >= 2:
                            lines.append(c)
                if os.path.exists(tess_tmp):
                    try:
                        os.remove(tess_tmp)
                    except Exception:
                        pass
                confidences = [75.0] * len(lines)
            except Exception as te:
                logger.error(f"Tesseract fallback error: {te}")

        # Clean duplicates preserving order
        unique_lines = []
        for line in lines:
            if line not in unique_lines:
                unique_lines.append(line)

        raw_text = "\n".join(unique_lines).strip()
        avg_conf = float(sum(confidences) / len(confidences)) if confidences else (80.0 if unique_lines else 0.0)

        uncertainty_flags = []
        if avg_conf < 60.0 and len(raw_text) > 0:
            uncertainty_flags.append(f"Low overall OCR confidence ({avg_conf:.1f}%). Findings should be manually reviewed.")
        elif not raw_text:
            uncertainty_flags.append("No readable text recognized by OCR on label image.")

        return {
            "raw_text": raw_text,
            "confidence_avg": round(avg_conf, 2),
            "words_detected": len(raw_text.split()),
            "low_confidence_word_count": sum(1 for c in confidences if c < 60.0),
            "uncertain_flags": uncertainty_flags,
        }
