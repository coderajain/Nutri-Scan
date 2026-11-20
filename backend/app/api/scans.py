"""Product label scan workflow endpoints (SCAN-001 through SCAN-006, OCR, Rules, Scoring, PDF)."""
import os
import re
import time
import uuid
import aiofiles
from typing import Optional, Union
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
from app.schemas.scan import ScanDetailResponse, ScanSummaryResponse, BatchScanResponse
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


async def _execute_scan_pipeline(
    upload_files: list[UploadFile],
    product_name: Optional[str],
    brand_name: Optional[str],
    rule_version_tag: str,
    db: Session,
    current_user: User,
    request: Optional[Request] = None,
) -> dict:
    """Core scanning pipeline executing OpenCV, Barcode, OCR, Rules, Scoring, and PDF."""
    start_time = time.time()

    if not upload_files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No packaging images provided for scanning.",
        )

    # 1. Input Validation across all files
    for f in upload_files:
        if f.content_type not in settings.ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format '{f.content_type}'. Allowed: JPG, JPEG, PNG, WEBP.",
            )

    # 2. Retrieve Rule Version
    rule_version = db.query(RuleVersion).filter(
        RuleVersion.version_tag == rule_version_tag,
        RuleVersion.is_active == True,
    ).first()
    if not rule_version:
        rule_version = db.query(RuleVersion).filter(RuleVersion.is_active == True).first()
        if not rule_version:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No active regulatory rule version available in system.",
            )

    # 3. Secure Evidence Storage (Isolated directory)
    scan_uuid = str(uuid.uuid4())
    evidence_dir = settings.EVIDENCE_DIR
    os.makedirs(evidence_dir, exist_ok=True)

    raw_paths = []
    proc_paths = []
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    for idx, f in enumerate(upload_files):
        ext = os.path.splitext(f.filename or "image.jpg")[1].lower()
        if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
            ext = ".jpg"
        raw_p = os.path.join(evidence_dir, f"{scan_uuid}_raw_{idx}{ext}")
        proc_p = os.path.join(evidence_dir, f"{scan_uuid}_proc_{idx}.png")

        file_bytes_read = 0
        async with aiofiles.open(raw_p, "wb") as out_file:
            while content := await f.read(1024 * 1024):
                file_bytes_read += len(content)
                if file_bytes_read > max_bytes:
                    await out_file.close()
                    if os.path.exists(raw_p):
                        os.remove(raw_p)
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB.",
                    )
                await out_file.write(content)

        raw_paths.append(raw_p)
        proc_paths.append(proc_p)

    primary_raw_path = raw_paths[0]
    primary_proc_path = proc_paths[0]
    pdf_file_path = os.path.join(evidence_dir, f"{scan_uuid}_report.pdf")

    # 4. Create Initial Pending Scan Record
    scan = Scan(
        id=scan_uuid,
        user_id=current_user.id,
        rule_version_id=rule_version.id,
        product_name=product_name,
        brand_name=brand_name,
        category="packaged_food",
        original_image_path=primary_raw_path,
        processed_image_path=primary_proc_path,
        pdf_report_path=pdf_file_path,
        overall_status=ScanStatus.PROCESSING,
    )
    db.add(scan)
    db.commit()

    try:
        all_ocr_lines = []
        all_confidences = []
        all_uncertainties = []
        merged_barcodes = []
        merged_qrs = []

        # 5. Process each uploaded packaging face
        for idx, (raw_p, proc_p) in enumerate(zip(raw_paths, proc_paths)):
            # Preprocess image with OpenCV
            ImageProcessor.preprocess_image(raw_p, proc_p)

            # Barcode and QR code detection
            bc_res = BarcodeScanner.scan(raw_p)
            for b in bc_res.get("barcodes", []):
                if b["code"] not in [x["code"] for x in merged_barcodes]:
                    merged_barcodes.append(b)
            for q in bc_res.get("qr_codes", []):
                if q["data"] not in [x["data"] for x in merged_qrs]:
                    merged_qrs.append(q)

            # OCR Multi-Pass
            ocr_engine = OCREngine()
            ocr_res = ocr_engine.extract_text(proc_p, raw_image_path=raw_p)
            if ocr_res.get("raw_text"):
                header = f"--- Packaging Face {idx + 1} ---" if len(raw_paths) > 1 else ""
                all_ocr_lines.append(f"{header}\n{ocr_res['raw_text']}".strip())
            if ocr_res.get("confidence_avg", 0) > 0:
                all_confidences.append(ocr_res["confidence_avg"])
            if ocr_res.get("uncertain_flags"):
                all_uncertainties.extend(ocr_res["uncertain_flags"])

        combined_raw_text = "\n\n".join(all_ocr_lines).strip()
        avg_ocr_conf = round(sum(all_confidences) / len(all_confidences), 2) if all_confidences else 0.0

        scan.ocr_raw_text = combined_raw_text
        scan.ocr_confidence_avg = avg_ocr_conf
        scan.uncertainty_flags = list(set(all_uncertainties))

        # 6. Structured Field Extraction
        extracted = FieldExtractor.extract_all(combined_raw_text)

        # Attach detected Barcode & QR Code into declarations
        primary_bc = merged_barcodes[0]["code"] if merged_barcodes else None
        primary_bc_fmt = merged_barcodes[0]["format"] if merged_barcodes else None
        primary_bc_country = merged_barcodes[0]["country"] if merged_barcodes else None
        primary_qr = merged_qrs[0]["data"] if merged_qrs else None

        if primary_bc:
            extracted["declarations"]["barcode"] = {
                "raw_value": primary_bc,
                "normalized_value": f"{primary_bc} ({primary_bc_fmt}, {primary_bc_country})",
                "unit": primary_bc_fmt,
                "confidence": 100.0,
                "metadata_payload": {
                    "primary_barcode": primary_bc,
                    "primary_barcode_format": primary_bc_fmt,
                    "primary_barcode_country": primary_bc_country,
                    "barcodes": merged_barcodes,
                },
            }

        if primary_qr:
            extracted["declarations"]["qr_code"] = {
                "raw_value": primary_qr,
                "normalized_value": primary_qr,
                "unit": "QR",
                "confidence": 100.0,
                "metadata_payload": {"qr_codes": merged_qrs},
            }
            # Enrich batch number, mfg date, and expiry date from decoded QR string (QR is tamper-proof)
            batch_qr = re.search(r'b\.?no\.?[\s\.:\-_]*([A-Za-z0-9\-_]+)', primary_qr, re.IGNORECASE)
            if batch_qr:
                extracted["declarations"]["batch_number"] = {
                    "raw_value": batch_qr.group(0).strip(),
                    "normalized_value": batch_qr.group(1).strip(),
                    "confidence": 100.0,
                }
            mfg_qr = re.search(r'mfg\.?dt\.?[\s\.:\-_]*(\d{1,2}[\/\.-]\d{1,2}[\/\.-]\d{2,4})', primary_qr, re.IGNORECASE)
            if mfg_qr:
                extracted["declarations"]["mfg_date"] = {
                    "raw_value": mfg_qr.group(0).strip(),
                    "normalized_value": mfg_qr.group(1).strip(),
                    "confidence": 100.0,
                }
            exp_qr = re.search(r'exp\.?dt\.?[\s\.:\-_]*(\d{1,2}[\/\.-]\d{1,2}[\/\.-]\d{2,4})', primary_qr, re.IGNORECASE)
            if exp_qr:
                extracted["declarations"]["expiry_date"] = {
                    "raw_value": exp_qr.group(0).strip(),
                    "normalized_value": exp_qr.group(1).strip(),
                    "confidence": 100.0,
                }

        # If product_name was not provided, take from OCR
        if not scan.product_name and extracted["declarations"].get("product_name"):
            scan.product_name = extracted["declarations"]["product_name"]["normalized_value"]
        if not scan.brand_name and extracted["declarations"].get("brand_name"):
            scan.brand_name = extracted["declarations"]["brand_name"]["normalized_value"]

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
                    confidence_score=val_dict.get("confidence", avg_ocr_conf),
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
                confidence_score=nut_val.get("confidence", avg_ocr_conf) if nut_val else None,
                is_present=nut_val is not None,
                is_readable=nut_val is not None,
                extraction_method="table_parser",
            )
            db.add(db_field)

        # 7. Compliance and Nutrition Evaluation
        lm_findings_raw = ComplianceEngine.evaluate(rule_version.rules, extracted)
        nutrition_findings_raw, nutrition_metrics = NutritionEngine.analyze(
            extracted["nutrition"], extracted["ingredients"]
        )
        all_findings_raw = lm_findings_raw + nutrition_findings_raw

        # 8. Scoring & Authenticity Verification
        compliance_score, comp_status, has_manual_flags = ScoringEngine.calculate_compliance_score(lm_findings_raw)
        nutrition_score, nut_status, is_insufficient = ScoringEngine.calculate_nutrition_score(
            extracted["nutrition"],
            nutrition_findings_raw,
            nutrition_metrics["nutrients_present_count"],
        )
        auth_score, auth_status, auth_breakdown = ScoringEngine.calculate_authenticity_score(
            declarations=extracted["declarations"],
            findings=all_findings_raw,
            barcode=primary_bc,
            qr_code=primary_qr,
            ocr_conf=avg_ocr_conf,
        )

        scan.compliance_score = compliance_score
        scan.compliance_status = comp_status
        scan.nutrition_score = nutrition_score
        scan.nutrition_status = nut_status
        scan.authenticity_score = auth_score
        scan.authenticity_status = auth_status
        scan.authenticity_breakdown = auth_breakdown
        scan.has_font_size_flags = has_manual_flags
        scan.is_data_insufficient = is_insufficient
        scan.overall_status = ScanStatus.COMPLETED

        # Persist findings
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

        # 9. Generate Evidence-Backed PDF Report
        PDFReportGenerator.generate_pdf(
            scan_id=scan.id,
            product_name=scan.product_name or "Packaged Commodity",
            rule_version_tag=rule_version.version_tag,
            compliance_score=compliance_score,
            nutrition_score=nutrition_score,
            compliance_status=comp_status.value,
            nutrition_status=nut_status.value,
            findings=all_findings_raw,
            original_image_path=primary_raw_path,
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
                "faces_scanned": len(raw_paths),
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


@router.post("/upload", response_model=ScanDetailResponse)
async def upload_and_process_scan(
    request: Request,
    file: Optional[UploadFile] = File(None),
    product_name: Optional[str] = Form(None),
    brand_name: Optional[str] = Form(None),
    rule_version_tag: str = Form("LM-PC-2011-v1.0"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload and analyze packaging images (supports single image or multiple faces for one product).
    Accepts files from form data under 'files', 'file', 'images', or 'image'.
    """
    form_data = await request.form()
    upload_files = []

    # Priority 1: Direct 'file' parameter if passed by client
    if file:
        upload_files.append(file)

    # Priority 2: Extract all files from 'files' and 'file' multi-value form fields
    for field_key in ("files", "file", "images", "image"):
        for item in form_data.getlist(field_key):
            if hasattr(item, "filename") and item.filename and item not in upload_files:
                upload_files.append(item)

    if not upload_files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No packaging image uploaded. Please select at least one image file.",
        )

    return await _execute_scan_pipeline(
        upload_files=upload_files,
        product_name=product_name,
        brand_name=brand_name,
        rule_version_tag=rule_version_tag,
        db=db,
        current_user=current_user,
        request=request,
    )


@router.post("/batch", response_model=BatchScanResponse)
async def upload_batch_scans(
    request: Request,
    rule_version_tag: str = Form("LM-PC-2011-v1.0"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Batch upload multiple separate products at once.
    Each file represents an individual product package.
    """
    form_data = await request.form()
    batch_files = []
    for field_key in ("files", "file", "images", "image"):
        for item in form_data.getlist(field_key):
            if hasattr(item, "filename") and item.filename and item not in batch_files:
                batch_files.append(item)

    if not batch_files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide at least one image file for batch processing.",
        )

    successful_scans = []
    failed_uploads = []

    for f in batch_files:
        try:
            detail = await _execute_scan_pipeline(
                upload_files=[f],
                product_name=None,
                brand_name=None,
                rule_version_tag=rule_version_tag,
                db=db,
                current_user=current_user,
                request=request,
            )
            successful_scans.append(detail)
        except Exception as exc:
            failed_uploads.append({
                "filename": f.filename or "unknown",
                "error": str(exc),
            })

    return {
        "total_uploaded": len(batch_files),
        "successful_scans": successful_scans,
        "failed_uploads": failed_uploads,
    }


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
    request: Request,
    index: int = 0,
    token: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Serves the preserved original evidence image by index (SCAN-003, SEC-007)."""
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found.")

    # Authenticate via Header or Query param
    user = None
    auth_header = request.headers.get("authorization")
    jwt_token = None
    if auth_header and auth_header.startswith("Bearer "):
        jwt_token = auth_header.split(" ")[1]
    elif token:
        jwt_token = token

    if jwt_token:
        try:
            payload = decode_access_token(jwt_token)
            user_id = payload.get("sub")
            if user_id:
                user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
        except Exception:
            pass

    if user and scan.user_id != user.id and user.role != UserRole.ADMINISTRATOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    target_path = scan.original_image_path
    if index > 0 and scan.original_image_path:
        ev_dir = os.path.dirname(scan.original_image_path)
        for ext in [".jpg", ".jpeg", ".png", ".webp"]:
            candidate = os.path.join(ev_dir, f"{scan.id}_raw_{index}{ext}")
            if os.path.exists(candidate):
                target_path = candidate
                break

    if not target_path or not os.path.exists(target_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidence image file not found.")

    ext = os.path.splitext(target_path)[1].lower()
    media_type = "image/jpeg" if ext in (".jpg", ".jpeg") else ("image/png" if ext == ".png" else "application/octet-stream")
    return FileResponse(path=target_path, media_type=media_type)


@router.get("/{scan_id}/processed-image")
def get_processed_evidence_image(
    scan_id: str,
    request: Request,
    index: int = 0,
    token: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Serves the enhanced processed image (SCAN-004)."""
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan or not scan.processed_image_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Processed image not found.")

    target_path = scan.processed_image_path
    if index > 0 and scan.processed_image_path:
        ev_dir = os.path.dirname(scan.processed_image_path)
        candidate = os.path.join(ev_dir, f"{scan.id}_proc_{index}.png")
        if os.path.exists(candidate):
            target_path = candidate

    if not os.path.exists(target_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Processed image not found.")
    return FileResponse(path=target_path, media_type="image/png")


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

    # Gather all evidence faces for this scan
    evidence_images = []
    if scan.original_image_path and os.path.exists(scan.original_image_path):
        evidence_images.append(f"/api/v1/scans/{scan.id}/image?index=0")

    ev_dir = os.path.dirname(scan.original_image_path) if scan.original_image_path else ""
    if ev_dir and os.path.exists(ev_dir):
        for i in range(1, 10):
            found = False
            for ext in [".jpg", ".jpeg", ".png", ".webp"]:
                candidate = os.path.join(ev_dir, f"{scan.id}_raw_{i}{ext}")
                if os.path.exists(candidate):
                    evidence_images.append(f"/api/v1/scans/{scan.id}/image?index={i}")
                    found = True
                    break
            if not found:
                break

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
        "authenticity_score": getattr(scan, "authenticity_score", None),
        "authenticity_status": getattr(scan, "authenticity_status", "inconclusive") or "inconclusive",
        "authenticity_breakdown": getattr(scan, "authenticity_breakdown", {}) or {},
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
        "processed_image_url": f"/api/v1/scans/{scan.id}/processed-image",
        "evidence_images": evidence_images,
        "pdf_report_url": f"/api/v1/scans/{scan.id}/report",
        "rule_version_tag": rule_version.version_tag if rule_version else None,
        "fields": scan.fields,
        "findings": scan.findings,
    }
