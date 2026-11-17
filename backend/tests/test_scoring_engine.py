"""Unit tests verifying separation of Compliance and Nutrition scores (SCORE-001, SCORE-002)."""
from app.services.scoring_engine import ScoringEngine
from app.models.finding import FindingType, FindingSeverity
from app.models.scan import ComplianceStatus, NutritionStatus


def test_separation_of_scores():
    """
    Verifies that a product can be 100% compliant in packaging law while
    having high risk in nutrition (SCORE-001, SCORE-002: independent scores).
    """
    # High compliance findings
    mock_lm_findings = [
        {"module": "legal_metrology", "finding_type": FindingType.PASS, "severity": FindingSeverity.CRITICAL},
        {"module": "legal_metrology", "finding_type": FindingType.PASS, "severity": FindingSeverity.CRITICAL},
        {"module": "legal_metrology", "finding_type": FindingType.PASS, "severity": FindingSeverity.MAJOR},
    ]

    comp_score, comp_status, has_manual = ScoringEngine.calculate_compliance_score(mock_lm_findings)
    assert comp_score == 100.0
    assert comp_status == ComplianceStatus.COMPLIANT

    # Poor nutrition findings (high sugar, high sat fat, high sodium)
    mock_nutri_findings = [
        {"module": "nutrition", "finding_type": FindingType.FAIL, "title": "High Sugar Content (>15g / 100g)"},
        {"module": "nutrition", "finding_type": FindingType.FAIL, "title": "High Saturated Fat (>5g / 100g)"},
        {"module": "nutrition", "finding_type": FindingType.FAIL, "title": "High Sodium Content (>600mg / 100g)"},
    ]
    mock_nutrition_table = {
        "energy_kcal": {"numeric_value": 500},
        "protein_g": {"numeric_value": 2.0},
        "total_sugars_g": {"numeric_value": 35.0},
    }

    nutri_score, nutri_status, is_insufficient = ScoringEngine.calculate_nutrition_score(
        mock_nutrition_table, mock_nutri_findings, nutrients_present_count=3
    )

    # 75 (base) - 20 (sugar) - 15 (sat fat) - 15 (sodium) = 25.0
    assert nutri_score == 25.0
    assert nutri_status == NutritionStatus.HIGH_RISK

    # SCORES ARE NEVER CONFLATED
    assert comp_score != nutri_score


def test_insufficient_nutrition_data():
    """Verifies that missing nutrition data triggers INSUFFICIENT_DATA status (SCORE-004)."""
    score, status, is_insufficient = ScoringEngine.calculate_nutrition_score(
        extracted_nutrition={},
        nutrition_findings=[],
        nutrients_present_count=1,  # Only 1 nutrient found
    )
    assert score is None
    assert status == NutritionStatus.INSUFFICIENT_DATA
    assert is_insufficient is True
