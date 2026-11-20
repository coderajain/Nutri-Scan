"""Barcode and QR code detection engine using native OpenCV (SCAN-005, LM-004)."""
import os
import cv2
import re
import logging
from typing import Optional

logger = logging.getLogger("nutriscan.services.barcode_scanner")

# GS1 Country Prefix Lookup Table
GS1_COUNTRY_PREFIXES = {
    "890": "India",
    "000": "USA / Canada", "001": "USA / Canada", "002": "USA / Canada", "003": "USA / Canada",
    "004": "USA / Canada", "005": "USA / Canada", "006": "USA / Canada", "007": "USA / Canada",
    "008": "USA / Canada", "009": "USA / Canada", "010": "USA / Canada", "011": "USA / Canada",
    "400": "Germany", "401": "Germany", "402": "Germany", "403": "Germany", "404": "Germany",
    "490": "Japan", "491": "Japan", "492": "Japan", "493": "Japan", "494": "Japan",
    "500": "United Kingdom", "501": "United Kingdom", "502": "United Kingdom", "503": "United Kingdom",
    "690": "China", "691": "China", "692": "China", "693": "China", "694": "China", "695": "China",
    "880": "South Korea",
    "885": "Thailand",
    "888": "Singapore",
    "893": "Vietnam",
    "930": "Australia", "931": "Australia", "932": "Australia",
}


class BarcodeScanner:
    """Detects and decodes 1D product barcodes (EAN-13, UPC-A, Code-128) and 2D QR codes."""

    @staticmethod
    def get_country_from_barcode(code: str) -> str:
        """Determines the GS1 member country origin from an EAN-13/UPC-A barcode."""
        clean_code = re.sub(r'[^0-9]', '', str(code))
        if len(clean_code) >= 3:
            prefix3 = clean_code[:3]
            if prefix3 in GS1_COUNTRY_PREFIXES:
                return f"{GS1_COUNTRY_PREFIXES[prefix3]} (GS1 prefix {prefix3})"
            prefix2 = clean_code[:2]
            if prefix2 in ("00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13"):
                return "USA / Canada"
        return "International / Unregistered"

    @classmethod
    def scan(cls, image_path: str) -> dict:
        """
        Scans an image for 1D barcodes and 2D QR codes across multiple orientations.
        Returns:
            {
                "has_barcode": bool,
                "has_qr": bool,
                "barcodes": list[dict],
                "qr_codes": list[dict],
                "primary_barcode": Optional[str],
                "primary_barcode_format": Optional[str],
                "primary_barcode_country": Optional[str],
                "primary_qr": Optional[str],
            }
        """
        if not os.path.exists(image_path):
            logger.warning(f"BarcodeScanner: image file not found: {image_path}")
            return cls._empty_result()

        img = cv2.imread(image_path)
        if img is None:
            return cls._empty_result()

        barcodes = []
        qr_codes = []
        seen_barcodes = set()
        seen_qrs = set()

        # Initialize native OpenCV detectors
        bc_detector = None
        try:
            bc_detector = cv2.barcode.BarcodeDetector()
        except Exception as e:
            logger.warning(f"cv2.barcode.BarcodeDetector not available: {e}")

        qr_detector = None
        try:
            qr_detector = cv2.QRCodeDetector()
        except Exception as e:
            logger.warning(f"cv2.QRCodeDetector not available: {e}")

        wechat_detector = None
        try:
            if hasattr(cv2, "wechat_qrcode_WeChatQRCode"):
                wechat_detector = cv2.wechat_qrcode_WeChatQRCode()
        except Exception as e:
            logger.debug(f"WeChatQRCode detector not available: {e}")

        # Scan across 0, 90, 180, and 270 degree rotations for curved/rotated packaging
        rotations = [
            (0, img),
            (90, cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)),
            (180, cv2.rotate(img, cv2.ROTATE_180)),
            (270, cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)),
        ]

        for angle, current_img in rotations:
            # 1. 1D Barcode Detection
            if bc_detector is not None:
                try:
                    res = bc_detector.detectAndDecode(current_img)
                    if res:
                        raw_code = res[0]
                        if raw_code and isinstance(raw_code, (str, bytes)):
                            code_str = str(raw_code).strip()
                            # Reject non-printable / control characters
                            code_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', code_str).strip()
                            if len(code_str) >= 8 and code_str not in seen_barcodes:
                                seen_barcodes.add(code_str)
                                fmt = "EAN-13" if len(code_str) == 13 else ("UPC-A" if len(code_str) == 12 else "CODE-128")
                                country = cls.get_country_from_barcode(code_str)
                                barcodes.append({
                                    "code": code_str,
                                    "format": fmt,
                                    "country": country,
                                    "angle_detected": angle,
                                })
                except Exception as exc:
                    logger.debug(f"Barcode detection pass failed at {angle}°: {exc}")

            # 2. 2D QR Code Detection (both standard and inverted passes)
            img_variants = [current_img]
            try:
                img_variants.append(cv2.bitwise_not(current_img))
            except Exception:
                pass

            for candidate_img in img_variants:
                # WeChat QR Detector pass (high sensitivity)
                if wechat_detector is not None:
                    try:
                        texts, pts = wechat_detector.detectAndDecode(candidate_img)
                        for t in texts:
                            if t and t.strip():
                                clean_t = t.strip()
                                if clean_t not in seen_qrs:
                                    seen_qrs.add(clean_t)
                                    is_url = clean_t.startswith("http://") or clean_t.startswith("https://")
                                    qr_codes.append({
                                        "data": clean_t,
                                        "type": "QR_CODE",
                                        "is_url": is_url,
                                        "angle_detected": angle,
                                    })
                    except Exception as wex:
                        logger.debug(f"WeChat QR pass failed at {angle}°: {wex}")

                # Standard OpenCV QR Detector pass
                if qr_detector is not None and not qr_codes:
                    try:
                        text, pts, _ = qr_detector.detectAndDecode(candidate_img)
                        if text and text.strip():
                            clean_text = text.strip()
                            if clean_text not in seen_qrs:
                                seen_qrs.add(clean_text)
                                is_url = clean_text.startswith("http://") or clean_text.startswith("https://")
                                qr_codes.append({
                                    "data": clean_text,
                                    "type": "QR_CODE",
                                    "is_url": is_url,
                                    "angle_detected": angle,
                                })
                    except Exception as exc:
                        logger.debug(f"QR detection pass failed at {angle}°: {exc}")

            # If both a barcode and a QR were already found, we can stop rotating
            if barcodes and qr_codes:
                break

        primary_bc = barcodes[0]["code"] if barcodes else None
        primary_bc_fmt = barcodes[0]["format"] if barcodes else None
        primary_bc_country = barcodes[0]["country"] if barcodes else None
        primary_qr = qr_codes[0]["data"] if qr_codes else None

        logger.info(f"Barcode/QR scan complete: {len(barcodes)} barcodes, {len(qr_codes)} QR codes found.")

        return {
            "has_barcode": len(barcodes) > 0,
            "has_qr": len(qr_codes) > 0,
            "barcodes": barcodes,
            "qr_codes": qr_codes,
            "primary_barcode": primary_bc,
            "primary_barcode_format": primary_bc_fmt,
            "primary_barcode_country": primary_bc_country,
            "primary_qr": primary_qr,
        }

    @staticmethod
    def _empty_result() -> dict:
        return {
            "has_barcode": False,
            "has_qr": False,
            "barcodes": [],
            "qr_codes": [],
            "primary_barcode": None,
            "primary_barcode_format": None,
            "primary_barcode_country": None,
            "primary_qr": None,
        }
