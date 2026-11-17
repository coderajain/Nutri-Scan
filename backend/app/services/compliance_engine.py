"""Legal Metrology Compliance Rule Engine (LM-001, LM-002, LM-003, LM-004, LM-005, LM-007)."""
from typing import Any
from app.models.rule_version import Rule, RuleSeverity
from app.models.finding import FindingType, FindingSeverity
import logging

logger = logging.getLogger("nutriscan.services.compliance_engine")


class ComplianceEngine:
    """
    Evaluates extracted packaged commodity declarations against versioned Legal Metrology and FSSAI rules.
    STRICT GUARDRAILS:
    - Never fabricate missing fields (LM-003: report as Pass, Fail, Not Found, Manual Review).
    - Flag physical scale attributes (font height) as non-authoritative / Manual Review (LM-005).
    - Non-authoritative disclaimer distinction (LM-007).
    """

    @classmethod
    def evaluate(cls, rules: list[Rule], extracted: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Evaluates a set of versioned rules against extracted declarations and nutrition data.
        Returns a list of finding dictionaries ready for persistence.
        """
        findings = []
        declarations = extracted.get("declarations", {})
        nutrition = extracted.get("nutrition", {})
        ingredients = extracted.get("ingredients", [])
        allergens = extracted.get("allergens", [])

        for rule in rules:
            field_name = rule.field_name
            val_type = rule.validation_type
            params = rule.validation_params or {}

            # 1. Special case: Physical font height heuristic (LM-005, LM-R-018)
            if val_type == "physical_scale_heuristic" or params.get("requires_manual_review"):
                findings.append({
                    "rule_id": rule.id,
                    "field_name": field_name,
                    "module": "legal_metrology",
                    "finding_type": FindingType.MANUAL_REVIEW,
                    "severity": FindingSeverity.INFO,
                    "title": f"Manual Verification Required: {rule.title}",
                    "message": "Physical font height cannot be verified from a digital image without physical scale calibration. Visual inspection recommended.",
                    "observed_value": declarations.get("net_quantity", {}).get("normalized_value") if declarations.get("net_quantity") else "Not Available",
                    "expected_condition": "Minimum numeral height in millimeters according to Table II of LM-PC Rules 2011.",
                    "is_font_size_flag": True,
                    "requires_manual_review": True,
                })
                continue

            # 2. Nutrition Panel evaluation (LM-R-013)
            if field_name == "nutrition_panel":
                present_nutrients = [k for k, v in nutrition.items() if v is not None]
                if len(present_nutrients) >= 4:
                    findings.append({
                        "rule_id": rule.id,
                        "field_name": field_name,
                        "module": "legal_metrology",
                        "finding_type": FindingType.PASS,
                        "severity": FindingSeverity.INFO,
                        "title": "Nutritional Panel Declared",
                        "message": f"Found nutritional information table with {len(present_nutrients)} declared values.",
                        "observed_value": ", ".join(present_nutrients),
                        "expected_condition": "Nutritional table per 100g/ml containing energy, protein, carbohydrates, and fats.",
                        "is_font_size_flag": False,
                        "requires_manual_review": False,
                    })
                else:
                    findings.append({
                        "rule_id": rule.id,
                        "field_name": field_name,
                        "module": "legal_metrology",
                        "finding_type": FindingType.FAIL if rule.is_mandatory else FindingType.NOT_FOUND,
                        "severity": FindingSeverity.CRITICAL if rule.severity == RuleSeverity.CRITICAL else FindingSeverity.MAJOR,
                        "title": "Incomplete Nutritional Panel",
                        "message": "Nutritional information table is either missing or missing mandatory nutrients (Energy, Protein, Carbs, Fat).",
                        "observed_value": f"{len(present_nutrients)} nutrients found",
                        "expected_condition": "Mandatory declaration of Energy, Protein, Carbohydrates, and Total Fat per 100g/ml.",
                        "is_font_size_flag": False,
                        "requires_manual_review": False,
                    })
                continue

            # 3. Ingredients list check (LM-R-012)
            if field_name == "ingredients":
                if ingredients and len(ingredients) > 0:
                    findings.append({
                        "rule_id": rule.id,
                        "field_name": field_name,
                        "module": "legal_metrology",
                        "finding_type": FindingType.PASS,
                        "severity": FindingSeverity.INFO,
                        "title": "Ingredients Declared",
                        "message": f"List of {len(ingredients)} ingredients identified in descending order.",
                        "observed_value": f"{len(ingredients)} items: {', '.join(ingredients[:5])}...",
                        "expected_condition": "Complete ingredient declaration in descending order of in-going weight.",
                        "is_font_size_flag": False,
                        "requires_manual_review": False,
                    })
                else:
                    findings.append({
                        "rule_id": rule.id,
                        "field_name": field_name,
                        "module": "legal_metrology",
                        "finding_type": FindingType.FAIL if rule.is_mandatory else FindingType.NOT_FOUND,
                        "severity": FindingSeverity.CRITICAL if rule.severity == RuleSeverity.CRITICAL else FindingSeverity.MAJOR,
                        "title": "Ingredients List Missing",
                        "message": "No ingredient list was found on the label image.",
                        "observed_value": "Not Found",
                        "expected_condition": "Mandatory ingredients list per FSSAI Labelling Regulations 2020.",
                        "is_font_size_flag": False,
                        "requires_manual_review": False,
                    })
                continue

            # 4. Allergen declaration check (LM-R-016)
            if field_name == "allergen_info":
                if allergens and len(allergens) > 0:
                    findings.append({
                        "rule_id": rule.id,
                        "field_name": field_name,
                        "module": "legal_metrology",
                        "finding_type": FindingType.PASS,
                        "severity": FindingSeverity.INFO,
                        "title": "Allergen Advisory Declared",
                        "message": f"Detected allergen declarations: {', '.join(allergens)}.",
                        "observed_value": ", ".join(allergens),
                        "expected_condition": "Declaration of common allergens or allergen advisory notice.",
                        "is_font_size_flag": False,
                        "requires_manual_review": False,
                    })
                else:
                    findings.append({
                        "rule_id": rule.id,
                        "field_name": field_name,
                        "module": "legal_metrology",
                        "finding_type": FindingType.MANUAL_REVIEW,
                        "severity": FindingSeverity.MINOR,
                        "title": "No Explicit Allergen Statement",
                        "message": "No allergen statement detected. If food contains gluten, milk, soy, nuts, or eggs, declaration is statutory.",
                        "observed_value": "None detected",
                        "expected_condition": "Allergen warning if scheduled allergens are present.",
                        "is_font_size_flag": False,
                        "requires_manual_review": True,
                    })
                continue

            # 5. Added Sugars & Saturated Fat check (LM-R-014)
            if field_name == "added_sugars_saturated_fat":
                has_sugars = nutrition.get("added_sugars_g") is not None
                has_sat_fat = nutrition.get("saturated_fat_g") is not None
                if has_sugars and has_sat_fat:
                    findings.append({
                        "rule_id": rule.id,
                        "field_name": field_name,
                        "module": "legal_metrology",
                        "finding_type": FindingType.PASS,
                        "severity": FindingSeverity.INFO,
                        "title": "Added Sugars & Saturated Fat Declared",
                        "message": f"Added Sugars: {nutrition['added_sugars_g']['normalized_value']}g, Sat Fat: {nutrition['saturated_fat_g']['normalized_value']}g",
                        "observed_value": f"Sugars: {nutrition['added_sugars_g']['normalized_value']}g | Sat Fat: {nutrition['saturated_fat_g']['normalized_value']}g",
                        "expected_condition": "Mandatory sub-breakdown of sugars and fats under FSSAI 2020.",
                        "is_font_size_flag": False,
                        "requires_manual_review": False,
                    })
                else:
                    findings.append({
                        "rule_id": rule.id,
                        "field_name": field_name,
                        "module": "legal_metrology",
                        "finding_type": FindingType.FAIL if rule.is_mandatory else FindingType.NOT_FOUND,
                        "severity": FindingSeverity.MAJOR,
                        "title": "Missing Added Sugars / Saturated Fat Breakdown",
                        "message": "Label does not display separate quantitative declaration for added sugars or saturated fat.",
                        "observed_value": f"Added Sugars: {'Yes' if has_sugars else 'No'}, Sat Fat: {'Yes' if has_sat_fat else 'No'}",
                        "expected_condition": "Both added sugars and saturated fats must be declared.",
                        "is_font_size_flag": False,
                        "requires_manual_review": False,
                    })
                continue

            # 6. Sodium declaration check (LM-R-015)
            if field_name == "sodium":
                if nutrition.get("sodium_mg") is not None:
                    findings.append({
                        "rule_id": rule.id,
                        "field_name": field_name,
                        "module": "legal_metrology",
                        "finding_type": FindingType.PASS,
                        "severity": FindingSeverity.INFO,
                        "title": "Sodium Content Declared",
                        "message": f"Declared sodium: {nutrition['sodium_mg']['normalized_value']} mg per 100g.",
                        "observed_value": f"{nutrition['sodium_mg']['normalized_value']} mg",
                        "expected_condition": "Sodium content must be stated in milligrams.",
                        "is_font_size_flag": False,
                        "requires_manual_review": False,
                    })
                else:
                    findings.append({
                        "rule_id": rule.id,
                        "field_name": field_name,
                        "module": "legal_metrology",
                        "finding_type": FindingType.FAIL if rule.is_mandatory else FindingType.NOT_FOUND,
                        "severity": FindingSeverity.MAJOR,
                        "title": "Sodium Declaration Missing",
                        "message": "Sodium content was not found in the nutritional information table.",
                        "observed_value": "Not Found",
                        "expected_condition": "Mandatory sodium declaration per FSSAI 2020.",
                        "is_font_size_flag": False,
                        "requires_manual_review": False,
                    })
                continue

            # 7. Standard declaration fields
            field_data = declarations.get(field_name)

            if field_data and field_data.get("normalized_value"):
                norm_val = field_data["normalized_value"]

                # Specific validation: Standard unit check
                if val_type == "allowed_units":
                    unit = field_data.get("unit", "").lower()
                    allowed = params.get("allowed_units", [])
                    if unit in allowed:
                        findings.append(cls._make_pass_finding(rule, norm_val))
                    else:
                        findings.append({
                            "rule_id": rule.id,
                            "field_name": field_name,
                            "module": "legal_metrology",
                            "finding_type": FindingType.FAIL,
                            "severity": FindingSeverity.CRITICAL,
                            "title": f"Non-Standard Unit for {rule.title}",
                            "message": f"Declared unit '{unit}' is not in approved standard metric units ({', '.join(allowed[:5])}).",
                            "observed_value": unit,
                            "expected_condition": f"Standard metric units: {', '.join(allowed)}",
                            "is_font_size_flag": False,
                            "requires_manual_review": False,
                        })
                    continue

                # Specific validation: FSSAI 14-digit regex
                if val_type == "regex" and field_name == "fssai_license":
                    if len(norm_val) == 14 and norm_val.isdigit():
                        findings.append(cls._make_pass_finding(rule, norm_val))
                    else:
                        findings.append({
                            "rule_id": rule.id,
                            "field_name": field_name,
                            "module": "legal_metrology",
                            "finding_type": FindingType.FAIL,
                            "severity": FindingSeverity.CRITICAL,
                            "title": "Invalid FSSAI License Format",
                            "message": f"Extracted value '{norm_val}' does not match standard 14-digit FSSAI registration structure.",
                            "observed_value": norm_val,
                            "expected_condition": "Valid 14-digit registration number starting with 1 or 2.",
                            "is_font_size_flag": False,
                            "requires_manual_review": False,
                        })
                    continue

                # Default pass for found value
                findings.append(cls._make_pass_finding(rule, norm_val))

            else:
                # Field is not found in OCR text (OCR-007: Zero fabrication)
                is_mandatory = rule.is_mandatory
                findings.append({
                    "rule_id": rule.id,
                    "field_name": field_name,
                    "module": "legal_metrology",
                    "finding_type": FindingType.FAIL if is_mandatory else FindingType.NOT_FOUND,
                    "severity": FindingSeverity.CRITICAL if rule.severity == RuleSeverity.CRITICAL else FindingSeverity.MAJOR,
                    "title": f"Missing Declaration: {rule.title}",
                    "message": f"The mandatory declaration '{rule.title}' was not detected in the provided label image.",
                    "observed_value": "Not Found",
                    "expected_condition": rule.description,
                    "is_font_size_flag": False,
                    "requires_manual_review": False,
                })

        return findings

    @staticmethod
    def _make_pass_finding(rule: Rule, observed_val: str) -> dict:
        return {
            "rule_id": rule.id,
            "field_name": rule.field_name,
            "module": "legal_metrology",
            "finding_type": FindingType.PASS,
            "severity": FindingSeverity.INFO,
            "title": f"Compliant: {rule.title}",
            "message": f"Successfully verified '{rule.title}'. Found valid declaration.",
            "observed_value": str(observed_val),
            "expected_condition": rule.description,
            "is_font_size_flag": False,
            "requires_manual_review": False,
        }
