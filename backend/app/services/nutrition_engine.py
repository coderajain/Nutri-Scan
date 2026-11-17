"""Nutrition and Ingredient Profiling Engine (NUT-001, NUT-004, NUT-005, NUT-006, SAF-002)."""
from typing import Any
from app.models.finding import FindingType, FindingSeverity
import logging

logger = logging.getLogger("nutriscan.services.nutrition_engine")

# Ultra-processed additive markers per INS (International Numbering System)
ADDITIVE_DATABASE = {
    "ins 211": {"name": "Sodium Benzoate", "type": "Preservative", "risk": "Common preservative; evaluate sensitivity"},
    "ins 202": {"name": "Potassium Sorbate", "type": "Preservative", "risk": "Antifungal preservative"},
    "ins 223": {"name": "Sodium Metabisulphite", "type": "Preservative/Antioxidant", "risk": "Sulphite warning for asthmatics"},
    "ins 621": {"name": "Monosodium Glutamate (MSG)", "type": "Flavour Enhancer", "risk": "Umami enhancer; advisory required"},
    "ins 951": {"name": "Aspartame", "type": "Artificial Sweetener", "risk": "Phenylketonurics warning required"},
    "ins 955": {"name": "Sucralose", "type": "Artificial Sweetener", "risk": "Non-caloric high intensity sweetener"},
    "ins 150d": {"name": "Caramel IV (Sulphite Ammonia)", "type": "Food Colour", "risk": "Synthetic caramel colour"},
    "ins 102": {"name": "Tartrazine", "type": "Synthetic Colour", "risk": "Yellow food colour; potential hyperactivity link"},
    "ins 110": {"name": "Sunset Yellow FCF", "type": "Synthetic Colour", "risk": "Azo dye; requires statutory declaration"},
    "ins 471": {"name": "Mono- and Diglycerides of Fatty Acids", "type": "Emulsifier", "risk": "Vegetable or animal lipid stabilizer"},
    "palm oil": {"name": "Palm Oil / Palmolein", "type": "Fat Source", "risk": "High in saturated fatty acids (approx 50%)"},
    "hydrogenated": {"name": "Hydrogenated Vegetable Oils", "type": "Industrial Fat", "risk": "Potential industrial trans fatty acid source"},
}


class NutritionEngine:
    """
    Evaluates nutritional thresholds and ingredient additives based on ICMR-NIN & WHO dietary guidelines.
    STRICT GUARDRAIL (SAF-002, NUT-006):
    All outputs are strictly informational decision-support assessments, NOT medical diagnosis or personalized advice.
    """

    @classmethod
    def analyze(cls, extracted_nutrition: dict[str, Any], ingredients: list[str]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """
        Analyzes nutrition numbers and ingredients.
        Returns:
            (findings_list, summary_metrics)
        """
        findings = []
        metrics = {
            "sugar_category": "unknown",
            "fat_category": "unknown",
            "sodium_category": "unknown",
            "additives_detected": [],
            "nutrients_present_count": 0,
        }

        # 1. Evaluate Sugar per 100g
        sugars = extracted_nutrition.get("total_sugars_g") or extracted_nutrition.get("added_sugars_g")
        if sugars and sugars.get("numeric_value") is not None:
            val = sugars["numeric_value"]
            metrics["nutrients_present_count"] += 1
            if val > 15.0:
                metrics["sugar_category"] = "high"
                findings.append({
                    "rule_id": None,
                    "field_name": "total_sugars",
                    "module": "nutrition",
                    "finding_type": FindingType.FAIL,
                    "severity": FindingSeverity.MAJOR,
                    "title": "High Sugar Content (>15g / 100g)",
                    "message": f"Contains {val}g sugar per 100g. WHO and ICMR classify foods with >15g/100g as high in free sugars.",
                    "observed_value": f"{val} g",
                    "expected_condition": "<= 15.0 g / 100g recommended threshold",
                    "is_font_size_flag": False,
                    "requires_manual_review": False,
                })
            elif val > 5.0:
                metrics["sugar_category"] = "moderate"
                findings.append({
                    "rule_id": None,
                    "field_name": "total_sugars",
                    "module": "nutrition",
                    "finding_type": FindingType.INFO,
                    "severity": FindingSeverity.INFO,
                    "title": "Moderate Sugar Content",
                    "message": f"Contains {val}g sugar per 100g (Moderate dietary intake).",
                    "observed_value": f"{val} g",
                    "expected_condition": "5g - 15g / 100g (Moderate)",
                    "is_font_size_flag": False,
                    "requires_manual_review": False,
                })
            else:
                metrics["sugar_category"] = "low"
                findings.append({
                    "rule_id": None,
                    "field_name": "total_sugars",
                    "module": "nutrition",
                    "finding_type": FindingType.PASS,
                    "severity": FindingSeverity.INFO,
                    "title": "Low Sugar Content (<=5g / 100g)",
                    "message": f"Contains {val}g sugar per 100g. Compliant with healthy low-sugar profile.",
                    "observed_value": f"{val} g",
                    "expected_condition": "<= 5.0 g / 100g",
                    "is_font_size_flag": False,
                    "requires_manual_review": False,
                })

        # 2. Evaluate Saturated Fat per 100g
        sat_fat = extracted_nutrition.get("saturated_fat_g")
        if sat_fat and sat_fat.get("numeric_value") is not None:
            val = sat_fat["numeric_value"]
            metrics["nutrients_present_count"] += 1
            if val > 5.0:
                metrics["fat_category"] = "high"
                findings.append({
                    "rule_id": None,
                    "field_name": "saturated_fat",
                    "module": "nutrition",
                    "finding_type": FindingType.FAIL,
                    "severity": FindingSeverity.MAJOR,
                    "title": "High Saturated Fat (>5g / 100g)",
                    "message": f"Contains {val}g saturated fat per 100g. Excessive saturated fat intake is linked to cardiovascular health risks.",
                    "observed_value": f"{val} g",
                    "expected_condition": "<= 5.0 g / 100g",
                    "is_font_size_flag": False,
                    "requires_manual_review": False,
                })
            else:
                metrics["fat_category"] = "moderate_to_low"
                findings.append({
                    "rule_id": None,
                    "field_name": "saturated_fat",
                    "module": "nutrition",
                    "finding_type": FindingType.PASS,
                    "severity": FindingSeverity.INFO,
                    "title": "Healthy Saturated Fat Level",
                    "message": f"Contains {val}g saturated fat per 100g.",
                    "observed_value": f"{val} g",
                    "expected_condition": "<= 5.0 g / 100g",
                    "is_font_size_flag": False,
                    "requires_manual_review": False,
                })

        # 3. Evaluate Trans Fat (Zero Tolerance standard in India: <= 0.2g is legally trans-fat free)
        trans_fat = extracted_nutrition.get("trans_fat_g")
        if trans_fat and trans_fat.get("numeric_value") is not None:
            val = trans_fat["numeric_value"]
            metrics["nutrients_present_count"] += 1
            if val > 0.2:
                findings.append({
                    "rule_id": None,
                    "field_name": "trans_fat",
                    "module": "nutrition",
                    "finding_type": FindingType.FAIL,
                    "severity": FindingSeverity.CRITICAL,
                    "title": "Elevated Trans Fat Content",
                    "message": f"Contains {val}g trans fat per 100g. Exceeds FSSAI 'trans-fat free' claim limit of 0.2g.",
                    "observed_value": f"{val} g",
                    "expected_condition": "<= 0.2 g / 100g",
                    "is_font_size_flag": False,
                    "requires_manual_review": False,
                })
            else:
                findings.append({
                    "rule_id": None,
                    "field_name": "trans_fat",
                    "module": "nutrition",
                    "finding_type": FindingType.PASS,
                    "severity": FindingSeverity.INFO,
                    "title": "Negligible / Zero Trans Fat",
                    "message": f"Trans fat is within recommended dietary ceiling ({val}g).",
                    "observed_value": f"{val} g",
                    "expected_condition": "<= 0.2 g / 100g",
                    "is_font_size_flag": False,
                    "requires_manual_review": False,
                })

        # 4. Evaluate Sodium per 100g
        sodium = extracted_nutrition.get("sodium_mg")
        if sodium and sodium.get("numeric_value") is not None:
            val = sodium["numeric_value"]
            metrics["nutrients_present_count"] += 1
            if val > 600.0:
                metrics["sodium_category"] = "high"
                findings.append({
                    "rule_id": None,
                    "field_name": "sodium",
                    "module": "nutrition",
                    "finding_type": FindingType.FAIL,
                    "severity": FindingSeverity.MAJOR,
                    "title": "High Sodium Content (>600mg / 100g)",
                    "message": f"Contains {val}mg sodium per 100g. Represents substantial portion of ICMR Recommended Dietary Allowance (2000mg/day).",
                    "observed_value": f"{val} mg",
                    "expected_condition": "<= 600 mg / 100g",
                    "is_font_size_flag": False,
                    "requires_manual_review": False,
                })
            elif val > 120.0:
                metrics["sodium_category"] = "moderate"
                findings.append({
                    "rule_id": None,
                    "field_name": "sodium",
                    "module": "nutrition",
                    "finding_type": FindingType.INFO,
                    "severity": FindingSeverity.INFO,
                    "title": "Moderate Sodium Content",
                    "message": f"Contains {val}mg sodium per 100g.",
                    "observed_value": f"{val} mg",
                    "expected_condition": "120 - 600 mg / 100g",
                    "is_font_size_flag": False,
                    "requires_manual_review": False,
                })
            else:
                metrics["sodium_category"] = "low"
                findings.append({
                    "rule_id": None,
                    "field_name": "sodium",
                    "module": "nutrition",
                    "finding_type": FindingType.PASS,
                    "severity": FindingSeverity.INFO,
                    "title": "Low Sodium Content (<=120mg / 100g)",
                    "message": f"Contains {val}mg sodium per 100g (Cardiovascular-friendly sodium profile).",
                    "observed_value": f"{val} mg",
                    "expected_condition": "<= 120 mg / 100g",
                    "is_font_size_flag": False,
                    "requires_manual_review": False,
                })

        # 5. Ingredient Additives & Ultra-processed markers analysis
        for ing in ingredients:
            ing_lower = ing.lower()
            for code, info in ADDITIVE_DATABASE.items():
                if code in ing_lower:
                    metrics["additives_detected"].append(info["name"])
                    findings.append({
                        "rule_id": None,
                        "field_name": "ingredients",
                        "module": "nutrition",
                        "finding_type": FindingType.INFO,
                        "severity": FindingSeverity.INFO,
                        "title": f"Additive Identified: {info['name']}",
                        "message": f"Identified {info['type']}: {info['risk']}.",
                        "observed_value": ing,
                        "expected_condition": "Disclose additives per FSSAI regulations.",
                        "is_font_size_flag": False,
                        "requires_manual_review": False,
                    })

        return findings, metrics
