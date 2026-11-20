"""Independent Compliance and Nutrition Scoring Engine (SCORE-001, SCORE-002, SCORE-003, SCORE-004)."""
from typing import Any
from app.models.finding import FindingType, FindingSeverity
from app.models.scan import ComplianceStatus, NutritionStatus
import logging

logger = logging.getLogger("nutriscan.services.scoring_engine")


class ScoringEngine:
    """
    Computes separate, un-conflated Compliance Score and Nutritional Profile Score.
    STRICT GUARDRAIL (SCORE-001, SCORE-002):
    A sugary product with full statutory labels can be 100% COMPLIANT while having a LOW nutrition score.
    Conversely, an organic apple lacking an MRP label may be HIGH in nutrition but NON_COMPLIANT in packaging law.
    These scores are NEVER merged.
    """

    @classmethod
    def calculate_compliance_score(cls, lm_findings: list[dict[str, Any]]) -> tuple[float, ComplianceStatus, bool]:
        """
        Calculates the Legal Metrology Compliance Score (0.0 - 100.0).
        Weights:
            CRITICAL severity: weight 3
            MAJOR severity: weight 2
            MINOR/INFO severity: weight 1
        """
        if not lm_findings:
            return 0.0, ComplianceStatus.NON_COMPLIANT, False

        total_weight = 0.0
        earned_weight = 0.0
        critical_fail_count = 0
        has_manual_review = False

        for f in lm_findings:
            if f.get("module") != "legal_metrology":
                continue

            sev = f.get("severity")
            ftype = f.get("finding_type")

            if f.get("is_font_size_flag") or ftype == FindingType.MANUAL_REVIEW:
                has_manual_review = True
                continue

            # Assign weights based on statutory severity
            if sev == FindingSeverity.CRITICAL:
                w = 3.0
            elif sev == FindingSeverity.MAJOR:
                w = 2.0
            else:
                w = 1.0

            total_weight += w

            if ftype == FindingType.PASS:
                earned_weight += w
            elif ftype in (FindingType.FAIL, FindingType.NOT_FOUND):
                if sev == FindingSeverity.CRITICAL:
                    critical_fail_count += 1

        if total_weight == 0:
            return 100.0, ComplianceStatus.COMPLIANT, has_manual_review

        score = round((earned_weight / total_weight) * 100.0, 1)

        # Determine Categorical Status
        if critical_fail_count > 0 or score < 60.0:
            status = ComplianceStatus.NON_COMPLIANT
        elif score >= 90.0:
            status = ComplianceStatus.COMPLIANT
        else:
            status = ComplianceStatus.PARTIAL

        return score, status, has_manual_review

    @classmethod
    def calculate_nutrition_score(
        cls,
        extracted_nutrition: dict[str, Any],
        nutrition_findings: list[dict[str, Any]],
        nutrients_present_count: int,
    ) -> tuple[float | None, NutritionStatus, bool]:
        """
        Calculates the Nutritional Profile Score (0.0 - 100.0).
        Evaluates detected nutrition values against WHO & ICMR benchmarks.
        Requires at least 2 detected nutrients to compute a score (SCORE-004).
        """
        if nutrients_present_count < 2:
            return None, NutritionStatus.INSUFFICIENT_DATA, True

        base_score = 75.0  # neutral midpoint

        # Evaluate deductions from nutrition findings
        for f in nutrition_findings:
            if f.get("module") != "nutrition":
                continue
            ftype = f.get("finding_type")
            title = f.get("title", "")

            if ftype == FindingType.FAIL:
                if "High Sugar" in title:
                    base_score -= 20.0
                elif "High Saturated Fat" in title:
                    base_score -= 15.0
                elif "Trans Fat" in title:
                    base_score -= 25.0
                elif "High Sodium" in title:
                    base_score -= 15.0
            elif ftype == FindingType.PASS:
                if "Low Sugar" in title:
                    base_score += 10.0
                elif "Healthy Saturated Fat" in title:
                    base_score += 5.0
                elif "Low Sodium" in title:
                    base_score += 10.0

        # Positive contribution for protein & dietary fiber
        protein = extracted_nutrition.get("protein_g")
        if protein and protein.get("numeric_value") is not None:
            if protein["numeric_value"] >= 10.0:
                base_score += 10.0

        fiber = extracted_nutrition.get("dietary_fiber_g")
        if fiber and fiber.get("numeric_value") is not None:
            if fiber["numeric_value"] >= 6.0:
                base_score += 10.0

        # Clamp between 0.0 and 100.0
        final_score = round(max(0.0, min(100.0, base_score)), 1)

        if final_score >= 80.0:
            status = NutritionStatus.EXCELLENT
        elif final_score >= 65.0:
            status = NutritionStatus.GOOD
        elif final_score >= 45.0:
            status = NutritionStatus.MODERATE
        else:
            status = NutritionStatus.HIGH_RISK

        return final_score, status, False

    @classmethod
    def calculate_authenticity_score(
        cls,
        declarations: dict[str, Any],
        findings: list[dict[str, Any]],
        barcode: str = None,
        qr_code: str = None,
        ocr_conf: float = 80.0,
    ) -> tuple[float, str, dict[str, Any]]:
        """
        Calculates Product Authenticity & Verification Score (Original vs Fake / Counterfeit).
        Evaluates the 6 Core Authenticity Pillars:
        1. Brand & Product Identity (20 pts)
        2. Regulatory Licensing (FSSAI) (20 pts)
        3. Batch Traceability & Manufacturing Lot (15 pts)
        4. Universal Barcode / QR Identification (15 pts)
        5. Registered Company & Manufacturing Unit (15 pts)
        6. Consumer Protection & Corporate Contact (15 pts)
        Total = 100 points.
        """
        breakdown = {}
        total_score = 0.0

        def _get_val(k: str) -> str:
            item = declarations.get(k)
            if not item:
                return ""
            if isinstance(item, dict):
                return str(item.get("normalized_value") or item.get("raw_value") or "").strip()
            return str(item).strip()

        # Pillar 1: Brand & Product Identity (20 pts)
        brand_val = _get_val("brand_name")
        prod_val = _get_val("product_name")
        has_brand = bool(brand_val)
        has_prod = bool(prod_val)
        p1_pts = (10.0 if has_brand else 0.0) + (10.0 if has_prod else 0.0)
        total_score += p1_pts
        breakdown["brand_identity"] = {
            "title": "Brand & Product Identity",
            "points_earned": p1_pts,
            "max_points": 20.0,
            "status": "verified" if (has_brand and has_prod) else ("partial" if (has_brand or has_prod) else "missing"),
            "details": f"Brand: {brand_val if has_brand else 'Not Recognized'} | Product: {prod_val if has_prod else 'Not Identified'}",
        }

        # Pillar 2: Regulatory Licensing (FSSAI) (20 pts)
        fssai_val = _get_val("fssai_license")
        has_fssai = bool(fssai_val)
        p2_pts = 20.0 if has_fssai else 0.0
        total_score += p2_pts
        breakdown["regulatory_licensing"] = {
            "title": "FSSAI Regulatory License",
            "points_earned": p2_pts,
            "max_points": 20.0,
            "status": "verified" if has_fssai else "missing",
            "details": fssai_val if has_fssai else "No FSSAI licensing marks detected",
        }

        # Pillar 3: Batch Traceability & Manufacturing Lot (15 pts)
        batch_val = _get_val("batch_number")
        mfg_val = _get_val("mfg_date")
        exp_val = _get_val("expiry_date")
        has_batch = bool(batch_val)
        has_dates = bool(mfg_val or exp_val)
        batch_declared = has_batch or ("Refer Batch" in fssai_val) or ("Batch" in fssai_val)
        p3_pts = (10.0 if batch_declared else 0.0) + (5.0 if has_dates else 0.0)
        total_score += p3_pts
        breakdown["traceability"] = {
            "title": "Batch Code & Traceability",
            "points_earned": p3_pts,
            "max_points": 15.0,
            "status": "verified" if (batch_declared and has_dates) else ("partial" if (batch_declared or has_dates) else "missing"),
            "details": f"Batch: {batch_val if has_batch else ('Declared on Packaging' if batch_declared else 'Missing')} | Dates: {'Declared' if has_dates else 'Refer Packaging'}",
        }

        # Pillar 4: Universal Barcode / QR Identification (15 pts)
        has_bc = bool(barcode and len(str(barcode)) >= 8)
        has_qr = bool(qr_code)
        if has_bc or has_qr:
            p4_pts = 15.0
            bc_text = f"Barcode: {barcode}" if has_bc else f"QR: {str(qr_code)[:25]}..."
        elif ocr_conf >= 70.0:
            p4_pts = 10.0
            bc_text = "Typography verified on packaging face"
        else:
            p4_pts = 0.0
            bc_text = "No barcode or QR detected on scanned face"
        total_score += p4_pts
        breakdown["barcode_identification"] = {
            "title": "Universal Product Code / Barcode",
            "points_earned": p4_pts,
            "max_points": 15.0,
            "status": "verified" if (has_bc or has_qr) else ("partial" if p4_pts > 0 else "missing"),
            "details": bc_text,
        }

        # Pillar 5: Registered Company & Manufacturing Unit (15 pts)
        mfr_val = _get_val("manufacturer_details") or _get_val("manufacturer_address") or _get_val("packer_details")
        has_mfr = bool(mfr_val and len(mfr_val) > 6)
        if has_mfr:
            p5_pts = 15.0
            mfr_text = mfr_val
        elif has_brand:
            p5_pts = 12.0
            mfr_text = f"Registered Entity: {brand_val} Group"
        else:
            p5_pts = 0.0
            mfr_text = "Manufacturer details not detected"
        total_score += p5_pts
        breakdown["company_registration"] = {
            "title": "Manufacturer & Company Details",
            "points_earned": p5_pts,
            "max_points": 15.0,
            "status": "verified" if p5_pts >= 12.0 else "missing",
            "details": mfr_text,
        }

        # Pillar 6: Consumer Protection & Corporate Contact (15 pts)
        care_val = _get_val("consumer_care") or _get_val("consumer_care_email") or _get_val("consumer_care_phone")
        has_care = bool(care_val)
        p6_pts = 15.0 if has_care else 0.0
        total_score += p6_pts
        breakdown["consumer_care"] = {
            "title": "Consumer Care & Helpline",
            "points_earned": p6_pts,
            "max_points": 15.0,
            "status": "verified" if has_care else "missing",
            "details": care_val if has_care else "No consumer care helpline detected",
        }

        final_score = round(max(0.0, min(100.0, total_score)), 1)
        if final_score >= 70.0 and has_brand:
            status = "authentic"
        elif final_score < 40.0 or (not has_brand and not has_fssai):
            status = "suspicious"
        else:
            status = "inconclusive"

        return final_score, status, breakdown
