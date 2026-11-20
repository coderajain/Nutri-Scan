"""OCR Engine: High-speed Multi-Pass Tesseract 5.x with PaddleOCR fallback."""
import os
import shutil
import re
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
            logger.warning(f"PaddleOCR initialization failed: {e}. Using Tesseract.")
            _paddle_instance = False
    return _paddle_instance if _paddle_instance is not False else None


class OCREngine:
    """Multi-pass Tesseract OCR engine with intelligent line deduplication and PaddleOCR fallback."""

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
    def deduplicate_lines(raw_lines: list[str]) -> list[str]:
        """
        Deduplicates OCR lines while filtering noise:
        1. Discards lines without at least two alphanumeric characters.
        2. Discards lines that are exact or substring duplicates of existing lines.
        3. Replaces shorter fragments with longer, cleaner lines when detected.
        """
        unique_lines: list[str] = []
        for line in raw_lines:
            line_str = line.strip()
            if len(re.findall(r'[A-Za-z0-9]', line_str)) < 2:
                continue

            cleaned = re.sub(r'^[^\w\(\[\"\'₹~]+|[^\w\)\]\"\'%\.]+$', '', line_str).strip()
            if not cleaned or len(cleaned) < 2:
                continue

            already_present = False
            for i, existing in enumerate(unique_lines):
                if cleaned.lower() == existing.lower():
                    already_present = True
                    break
                if cleaned.lower() in existing.lower():
                    already_present = True
                    break
                if existing.lower() in cleaned.lower() and len(cleaned) > len(existing) + 3:
                    unique_lines[i] = cleaned
                    already_present = True
                    break

            if not already_present:
                unique_lines.append(cleaned)

        return unique_lines

    @staticmethod
    def group_boxes_into_rows(boxes, texts, scores) -> tuple[list[str], list[float]]:
        """Groups OCR bounding boxes by vertical Y-coordinate into clean rows."""
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
        High-precision multi-pass OCR pipeline:
        Pass 1: Tesseract PSM 3 on enhanced image (sparse declarations, dates, licenses, product name)
        Pass 2: Tesseract PSM 4 on natural grayscale image (multi-column tables, nutrition values, contacts)
        Pass 3: Tesseract PSM 6 on shadow-compensated preprocessed image (dense text blocks & declarations)
        Pass 4: Tesseract PSM 6 on zoomed nutrition table region (resolves small dense table numerals)
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found for OCR: {image_path}")

        raw_candidates: list[str] = []
        confidences: list[float] = []
        target_raw = raw_image_path if raw_image_path and os.path.exists(raw_image_path) else image_path

        # 1. Primary Engine: High-speed Multi-pass Tesseract 5.x
        if self.is_tesseract_available():
            try:
                import pytesseract

                # Pass 1: PSM 3 on enhanced image
                with Image.open(image_path) as img:
                    txt1 = pytesseract.image_to_string(img, config=r"--oem 1 --psm 3 -l eng")
                    raw_candidates.extend(txt1.splitlines())

                    data = pytesseract.image_to_data(img, config=r"--oem 1 --psm 3 -l eng", output_type=pytesseract.Output.DICT)
                    for i, word in enumerate(data.get("text", [])):
                        w = word.strip()
                        if w:
                            try:
                                conf = float(data["conf"][i])
                                if conf > 0:
                                    confidences.append(conf)
                            except (ValueError, TypeError):
                                pass

                # Pass 2: Natural grayscale multi-orientation scanning (handles normal, inverted 180°, and vertical 90°/270° packaging)
                img_cv = cv2.imread(target_raw)
                if img_cv is not None:
                    h, w = img_cv.shape[:2]
                    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                    txt_p4 = pytesseract.image_to_string(gray, config=r"--oem 1 --psm 4 -l eng")
                    raw_candidates.extend(txt_p4.splitlines())

                    # Pass 2b: 180-degree rotation (resolves inverted packaging, curved lids, and upside-down photos)
                    rot_180 = cv2.rotate(img_cv, cv2.ROTATE_180)
                    gray_180 = cv2.cvtColor(rot_180, cv2.COLOR_BGR2GRAY)
                    txt_180_p6 = pytesseract.image_to_string(gray_180, config=r"--oem 1 --psm 6 -l eng")
                    raw_candidates.extend(txt_180_p6.splitlines())
                    txt_180_p3 = pytesseract.image_to_string(gray_180, config=r"--oem 1 --psm 3 -l eng")
                    raw_candidates.extend(txt_180_p3.splitlines())

                    # Pass 2c: 90° & 270° rotations for vertical side-panels and rotated label faces
                    for rot_code in (cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_90_COUNTERCLOCKWISE):
                        rot_side = cv2.rotate(img_cv, rot_code)
                        gray_side = cv2.cvtColor(rot_side, cv2.COLOR_BGR2GRAY)
                        txt_side = pytesseract.image_to_string(gray_side, config=r"--oem 1 --psm 6 -l eng")
                        raw_candidates.extend(txt_side.splitlines())

                    # Pass 3: Nutrition table region zoom (bottom 48% with gamma adjustment)
                    if h >= 800:
                        crop = img_cv[int(h * 0.50):, :]
                        up = cv2.resize(crop, (0, 0), fx=1.8, fy=1.8, interpolation=cv2.INTER_CUBIC)
                        up_gray = cv2.cvtColor(up, cv2.COLOR_BGR2GRAY)
                        lut = np.array([((i / 255.0) ** (1.0 / 0.75)) * 255 for i in np.arange(0, 256)]).astype("uint8")
                        g_crop = cv2.LUT(up_gray, lut)
                        txt_tbl = pytesseract.image_to_string(g_crop, config=r"--oem 1 --psm 6 -l eng")
                        raw_candidates.extend(txt_tbl.splitlines())

                # Pass 4: PSM 6 on shadow-compensated image
                tess_tmp = image_path + "_tess_prep.png"
                try:
                    preprocess_for_tesseract(target_raw, tess_tmp)
                    with Image.open(tess_tmp) as t_img:
                        txt2 = pytesseract.image_to_string(t_img, config=r"--oem 1 --psm 6 -l eng")
                        raw_candidates.extend(txt2.splitlines())
                finally:
                    if os.path.exists(tess_tmp):
                        try:
                            os.remove(tess_tmp)
                        except Exception:
                            pass

            except Exception as te:
                logger.warning(f"Tesseract extraction error: {te}")

        # 2. Fallback Engine: PaddleOCR (only if Tesseract returned nothing)
        if not raw_candidates:
            paddle = get_paddle_ocr()
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
                                raw_candidates.extend(row_lines)
                                confidences.extend(row_confs)
                except Exception as e:
                    logger.warning(f"PaddleOCR fallback error: {e}")

        # Intelligent line deduplication & artifact suppression
        unique_lines = self.deduplicate_lines(raw_candidates)

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
