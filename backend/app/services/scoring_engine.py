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
        STRICT GUARDRAIL (SCORE-004):
        If fewer than 3 mandatory nutrients are declared, marks as INSUFFICIENT_DATA and returns score=None.
        """
        if nutrients_present_count < 3:
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
