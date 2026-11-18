"""Product label scan workflow endpoints (SCAN-001 through SCAN-006, OCR, Rules, Scoring, PDF)."""
import os
import time
import uuid
import aiofiles
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.config import settings
from app.models.user import User, UserRole
from app.models.rule_version import RuleVersion
from app.models.scan import Scan, ScanStatus
from app.models.scan_field import ScanField
from app.models.finding import Finding
from app.schemas.scan import ScanDetailResponse, ScanSummaryResponse
from app.api.deps import get_current_user, log_audit_event
from app.services.image_processor import ImageProcessor
from app.services.ocr_engine import OCREngine
from app.services.barcode_scanner import BarcodeScanner
from app.services.field_extractor import FieldExtractor
from app.services.compliance_engine import ComplianceEngine
from app.services.nutrition_engine import NutritionEngine
from app.services.scoring_engine import ScoringEngine
from app.services.report_generator import PDFReportGenerator
import logging

logger = logging.getLogger("nutriscan.api.scans")
router = APIRouter(prefix="/scans", tags=["Scanning & OCR"])


@router.post("/upload", response_model=ScanDetailResponse)
async def upload_and_process_scan(
    request: Request,
    file: UploadFile = File(...),
    product_name: str = Form(None),
    brand_name: str = Form(None),
    rule_version_tag: str = Form("LM-PC-2011-v1.0"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Main scan pipeline:
    1. Validates image type/size (SCAN-001, SCAN-002)
    2. Preserves original evidence (SCAN-003, SEC-006)
    3. OpenCV preprocessing (SCAN-004)
    4. Tesseract OCR (OCR-001)
    5. Information extraction (OCR-005)
    6. Compliance and nutrition analysis (LM-001, NUT-001)
    7. Independent scoring (SCORE-001, SCORE-002)
    8. PDF report generation (REP-001, REP-004)
    """
    start_time = time.time()

    # 1. Input Validation (SCAN-001, SCAN-002, SEC-004)
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{file.content_type}'. Allowed types: JPG, JPEG, PNG, WEBP.",
        )

    # 2. Retrieve Rule Version (LM-001, LM-006)
    rule_version = db.query(RuleVersion).filter(
        RuleVersion.version_tag == rule_version_tag,
        RuleVersion.is_active == True,
    ).first()
    if not rule_version:
        # Fallback to any active version
        rule_version = db.query(RuleVersion).filter(RuleVersion.is_active == True).first()
        if not rule_version:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No active regulatory rule version available in system.",
            )

    # 3. Secure Evidence Storage (SCAN-003, SEC-006)
    scan_uuid = str(uuid.uuid4())
    evidence_dir = settings.EVIDENCE_DIR
    os.makedirs(evidence_dir, exist_ok=True)

    file_ext = os.path.splitext(file.filename or "image.jpg")[1].lower()
    if file_ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        file_ext = ".jpg"

    original_filename = f"{scan_uuid}_raw{file_ext}"
    original_file_path = os.path.join(evidence_dir, original_filename)
    processed_filename = f"{scan_uuid}_proc.png"
    processed_file_path = os.path.join(evidence_dir, processed_filename)
    pdf_filename = f"{scan_uuid}_report.pdf"
    pdf_file_path = os.path.join(evidence_dir, pdf_filename)

    # Stream file to storage
    file_bytes_read = 0
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    async with aiofiles.open(original_file_path, "wb") as out_file:
        while content := await file.read(1024 * 1024):  # 1MB chunks
            file_bytes_read += len(content)
            if file_bytes_read > max_bytes:
                await out_file.close()
                if os.path.exists(original_file_path):
                    os.remove(original_file_path)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB.",
                )
            await out_file.write(content)

    # 4. Create Initial Pending Scan Record
    scan = Scan(
        id=scan_uuid,
        user_id=current_user.id,
        rule_version_id=rule_version.id,
        product_name=product_name,
        brand_name=brand_name,
        category="packaged_food",
        original_image_path=original_file_path,
        processed_image_path=processed_file_path,
        pdf_report_path=pdf_file_path,
        overall_status=ScanStatus.PROCESSING,
    )
    db.add(scan)
    db.commit()

    try:
        # 5. Image Preprocessing (SCAN-004)
        ImageProcessor.preprocess_image(original_file_path, processed_file_path)

        # 6. Barcode & QR Code Scanning (SCAN-005, LM-004)
        barcode_result = BarcodeScanner.scan(original_file_path)

        # 7. OCR Text Extraction (OCR-001, OCR-003) using multi-pass recognition
        ocr_engine = OCREngine()
        ocr_result = ocr_engine.extract_text(processed_file_path, raw_image_path=original_file_path)
        raw_text = ocr_result["raw_text"]
        ocr_conf = ocr_result["confidence_avg"]
        uncertainty_flags = ocr_result.get("uncertain_flags", [])

        scan.ocr_raw_text = raw_text
        scan.ocr_confidence_avg = ocr_conf
        scan.uncertainty_flags = uncertainty_flags

        # 8. Field Extraction (OCR-004, OCR-005, OCR-007, NUT-001, NUT-005)
        extracted = FieldExtractor.extract_all(raw_text)

        # Attach detected Barcode & QR Code into declarations
        if barcode_result.get("primary_barcode"):
            extracted["declarations"]["barcode"] = {
                "raw_value": barcode_result["primary_barcode"],
                "normalized_value": f"{barcode_result['primary_barcode']} ({barcode_result.get('primary_barcode_format', 'BARCODE')}, {barcode_result.get('primary_barcode_country', '')})",
                "unit": barcode_result.get("primary_barcode_format"),
                "confidence": 100.0,
                "metadata_payload": barcode_result,
            }

        if barcode_result.get("primary_qr"):
            extracted["declarations"]["qr_code"] = {
                "raw_value": barcode_result["primary_qr"],
                "normalized_value": barcode_result["primary_qr"],
                "unit": "QR",
                "confidence": 100.0,
                "metadata_payload": barcode_result,
            }

        # If product_name was not provided by user, take from OCR
        if not scan.product_name and extracted["declarations"].get("product_name"):
            scan.product_name = extracted["declarations"]["product_name"]["normalized_value"]

        # Persist extracted fields
        for field_name, val_dict in extracted["declarations"].items():
            if val_dict:
                db_field = ScanField(
                    scan_id=scan.id,
                    field_name=field_name,
                    field_category="declaration" if field_name not in ("barcode", "qr_code") else "identification",
                    raw_value=val_dict.get("raw_value"),
                    normalized_value=val_dict.get("normalized_value"),
                    unit=val_dict.get("unit"),
                    confidence_score=val_dict.get("confidence", ocr_conf),
                    is_present=True,
                    is_readable=True,
                    extraction_method="opencv_barcode" if field_name == "barcode" else ("opencv_qr" if field_name == "qr_code" else "regex_pattern"),
                    metadata_payload=val_dict.get("metadata_payload", {}),
                )
                db.add(db_field)

        for nut_key, nut_val in extracted["nutrition"].items():
            db_field = ScanField(
                scan_id=scan.id,
                field_name=nut_key,
                field_category="nutrition",
                raw_value=nut_val.get("raw_value") if nut_val else None,
                normalized_value=nut_val.get("normalized_value") if nut_val else None,
                unit=nut_val.get("unit") if nut_val else None,
                confidence_score=nut_val.get("confidence", ocr_conf) if nut_val else None,
                is_present=nut_val is not None,
                is_readable=nut_val is not None,
                extraction_method="table_parser",
            )
            db.add(db_field)

        # 8. Legal Metrology Compliance Rule Evaluation (LM-001 - LM-007)
        lm_findings_raw = ComplianceEngine.evaluate(rule_version.rules, extracted)

        # 9. Nutrition & Additive Analysis (NUT-001 - NUT-006, SAF-002)
        nutrition_findings_raw, nutrition_metrics = NutritionEngine.analyze(
            extracted["nutrition"], extracted["ingredients"]
        )

        all_findings_raw = lm_findings_raw + nutrition_findings_raw

        # 10. Scoring (SCORE-001, SCORE-002: Separated scores)
        compliance_score, comp_status, has_manual_flags = ScoringEngine.calculate_compliance_score(lm_findings_raw)
        nutrition_score, nut_status, is_insufficient = ScoringEngine.calculate_nutrition_score(
            extracted["nutrition"],
            nutrition_findings_raw,
            nutrition_metrics["nutrients_present_count"],
        )

        scan.compliance_score = compliance_score
        scan.compliance_status = comp_status
        scan.nutrition_score = nutrition_score
        scan.nutrition_status = nut_status
        scan.has_font_size_flags = has_manual_flags
        scan.is_data_insufficient = is_insufficient
        scan.overall_status = ScanStatus.COMPLETED

        # Persist findings
        persisted_findings = []
        for f in all_findings_raw:
            db_finding = Finding(
                scan_id=scan.id,
                rule_id=f.get("rule_id"),
                field_name=f["field_name"],
                module=f["module"],
                finding_type=f["finding_type"],
                severity=f["severity"],
                title=f["title"],
                message=f["message"],
                observed_value=f.get("observed_value"),
                expected_condition=f.get("expected_condition"),
                is_font_size_flag=f.get("is_font_size_flag", False),
                requires_manual_review=f.get("requires_manual_review", False),
            )
            db.add(db_finding)
            persisted_findings.append(db_finding)

        # 11. Generate PDF Report (REP-001, REP-004)
        PDFReportGenerator.generate_pdf(
            scan_id=scan.id,
            product_name=scan.product_name or "Packaged Commodity",
            rule_version_tag=rule_version.version_tag,
            compliance_score=compliance_score,
            nutrition_score=nutrition_score,
            compliance_status=comp_status.value,
            nutrition_status=nut_status.value,
            findings=all_findings_raw,
            original_image_path=original_file_path,
            output_pdf_path=pdf_file_path,
            created_at_str=datetime.utcnow().strftime("%d %b %Y, %H:%M UTC"),
        )

        scan.scan_duration_ms = int((time.time() - start_time) * 1000)
        scan.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(scan)

        log_audit_event(
            db=db,
            user=current_user,
            action="SCAN_PERFORMED",
            resource_type="scan",
            resource_id=scan.id,
            details={
                "compliance_score": compliance_score,
                "nutrition_score": nutrition_score,
                "rule_version": rule_version.version_tag,
            },
            request=request,
        )

        return _build_scan_detail_response(scan, rule_version)

    except Exception as exc:
        logger.error(f"Scan processing error: {exc}", exc_info=True)
        scan.overall_status = ScanStatus.FAILED
        scan.uncertainty_flags = [f"Processing error: {str(exc)}"]
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error occurred during OCR or compliance analysis. Original evidence is preserved.",
        )


@router.get("/{scan_id}", response_model=ScanDetailResponse)
def get_scan_detail(
    scan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieves full detail of a scan (HIS-005)."""
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found.")

    # Access control: users can only view their own scans unless admin (SEC-003, SEC-007)
    if scan.user_id != current_user.id and current_user.role != UserRole.ADMINISTRATOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this scan record.")

    return _build_scan_detail_response(scan, scan.rule_version)


@router.get("/{scan_id}/report")
def download_scan_report(
    scan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Downloads the generated evidence-backed PDF report (REP-004, REP-005)."""
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found.")

    if scan.user_id != current_user.id and current_user.role != UserRole.ADMINISTRATOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    if not scan.pdf_report_path or not os.path.exists(scan.pdf_report_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PDF report file not found on server.")

    return FileResponse(
        path=scan.pdf_report_path,
        filename=f"NutriScan_Audit_{scan.id[:8]}.pdf",
        media_type="application/pdf",
    )


@router.get("/{scan_id}/image")
def get_original_evidence_image(
    scan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Serves the preserved original evidence image (SCAN-003, SEC-007)."""
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found.")

    if scan.user_id != current_user.id and current_user.role != UserRole.ADMINISTRATOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    if not scan.original_image_path or not os.path.exists(scan.original_image_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidence image file not found.")

    return FileResponse(path=scan.original_image_path)


def _build_scan_detail_response(scan: Scan, rule_version: RuleVersion) -> dict:
    """Helper to assemble full ScanDetailResponse dictionary."""
    primary_bc = None
    bc_fmt = None
    bc_country = None
    primary_qr = None
    bc_meta = None

    for f in scan.fields:
        if f.field_name == "barcode" and f.is_present:
            primary_bc = f.raw_value
            bc_meta = f.metadata_payload or {}
            bc_fmt = bc_meta.get("primary_barcode_format") or f.unit or "EAN-13"
            bc_country = bc_meta.get("primary_barcode_country") or ("India" if str(primary_bc).startswith("890") else "International")
        elif f.field_name == "qr_code" and f.is_present:
            primary_qr = f.raw_value

    return {
        "id": scan.id,
        "user_id": scan.user_id,
        "rule_version_id": scan.rule_version_id,
        "product_name": scan.product_name,
        "brand_name": scan.brand_name,
        "category": scan.category,
        "overall_status": scan.overall_status,
        "compliance_status": scan.compliance_status,
        "nutrition_status": scan.nutrition_status,
        "compliance_score": scan.compliance_score,
        "nutrition_score": scan.nutrition_score,
        "has_font_size_flags": scan.has_font_size_flags,
        "is_data_insufficient": scan.is_data_insufficient,
        "ocr_confidence_avg": scan.ocr_confidence_avg,
        "ocr_raw_text": scan.ocr_raw_text,
        "uncertainty_flags": scan.uncertainty_flags or [],
        "barcode": primary_bc,
        "barcode_format": bc_fmt,
        "barcode_country": bc_country,
        "qr_code": primary_qr,
        "barcode_metadata": bc_meta,
        "scan_duration_ms": scan.scan_duration_ms,
        "created_at": scan.created_at,
        "completed_at": scan.completed_at,
        "original_image_url": f"/api/v1/scans/{scan.id}/image",
        "processed_image_url": None,
        "pdf_report_url": f"/api/v1/scans/{scan.id}/report",
        "rule_version_tag": rule_version.version_tag if rule_version else None,
        "fields": scan.fields,
        "findings": scan.findings,
    }
