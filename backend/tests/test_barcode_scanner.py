"""Unit tests for BarcodeScanner (SCAN-005, LM-004)."""
import pytest
from app.services.barcode_scanner import BarcodeScanner


def test_gs1_country_lookup():
    """Verifies GS1 country detection from EAN-13 prefix."""
    # India prefix (890)
    assert "India" in BarcodeScanner.get_country_from_barcode("8901262180115")
    # USA / Canada prefix (000-019)
    assert "USA" in BarcodeScanner.get_country_from_barcode("0012345678905")
    # Unknown prefix
    assert "International" in BarcodeScanner.get_country_from_barcode("9999999999999")


def test_barcode_scanner_nonexistent_file():
    """Verifies graceful handling of missing file."""
    res = BarcodeScanner.scan("non_existent_image.jpg")
    assert res["has_barcode"] is False
    assert res["has_qr"] is False
    assert res["barcodes"] == []
    assert res["qr_codes"] == []
