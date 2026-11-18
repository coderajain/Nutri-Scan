"""Structured label field extraction pipeline (OCR-004, OCR-005, OCR-007, NUT-001, NUT-005)."""
import re
from typing import Optional, Any
import logging

logger = logging.getLogger("nutriscan.services.field_extractor")


class FieldExtractor:
    """
    Extracts structured label declarations, ingredients, and nutrition values from raw OCR text.
    STRICT GUARDRAIL (OCR-007, SAF-003, NUT-005):
    Never fabricate or infer missing values. Values not present in OCR text remain None / Not Found.
    """

    @classmethod
    def extract_all(cls, raw_text: str) -> dict[str, Any]:
        """Runs all field extraction routines and returns a dictionary of extracted fields and metadata."""
        if not raw_text or not raw_text.strip():
            return {
                "declarations": {},
                "nutrition": {},
                "ingredients": [],
                "allergens": [],
                "raw_text_clean": "",
            }

        text = cls._clean_text(raw_text)

        declarations = {
            "product_name": cls._extract_product_name(text),
            "net_quantity": cls._extract_net_quantity(text),
            "net_quantity_unit": cls._extract_net_quantity_unit(text),
            "mrp": cls._extract_mrp(text),
            "manufacturer_details": cls._extract_manufacturer_details(text),
            "expiry_date": cls._extract_expiry_date(text),
            "mfg_date": cls._extract_mfg_date(text),
            "batch_number": cls._extract_batch_number(text),
            "fssai_license": cls._extract_fssai_license(text),
            "consumer_care": cls._extract_consumer_care(text),
            "country_of_origin": cls._extract_country_of_origin(text),
            "veg_nonveg_symbol": cls._extract_veg_symbol(text),
            "importer_details": cls._extract_importer_details(text),
            "storage_instructions": cls._extract_storage_instructions(text),
        }

        nutrition = cls._extract_nutrition_table(text)
        ingredients = cls._extract_ingredients_list(text)
        allergens = cls._extract_allergens(text, ingredients)

        return {
            "declarations": declarations,
            "nutrition": nutrition,
            "ingredients": ingredients,
            "allergens": allergens,
            "raw_text_clean": text,
        }

    @staticmethod
    def _clean_text(text: str) -> str:
        """Normalizes unicode whitespace, currency symbols, and line breaks."""
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        # Replace common OCR misreadings of Rupee symbol (do not replace pipe |)
        text = re.sub(r'[₹`]\s*', '₹ ', text)
        return text

    @classmethod
    def _extract_product_name(cls, text: str) -> Optional[dict]:
        """Extracts brand or product name, prioritizing clear product descriptors."""
        lines = [line.strip() for line in text.split("\n") if len(line.strip()) > 3]
        if not lines:
            return None

        # Look for explicit food/drink names or prominent non-metadata lines
        candidates = []
        for line in lines:
            if line.startswith(("-", "=", "*", "#")) or "packaging face" in line.lower():
                continue
            # Skip dates, timestamps, batch numbers, licenses, instructions, and addresses
            if re.match(r'^\d', line) or re.search(r'(\d{2}/\d{2}/\d{2,4}|:\d{2}|usp|shake|drink|fssai|lic|mrp|mfg|exp|batch|lot|net qty|regd|address|pvt|ltd|keep your|city clean|consumer)', line, re.IGNORECASE):
                continue
            if 4 <= len(line) <= 60:
                # High priority if it has product words (milk, beverage, snack, chips, chocolate, etc.)
                if re.search(r'(milk|flavoured|chocolate|hazelnut|shake|drink|juice|biscuit|cookie|tea|coffee|oil|water)', line, re.IGNORECASE):
                    return {
                        "raw_value": line,
                        "normalized_value": line.title(),
                        "confidence": 95.0,
                    }
                candidates.append(line)

        if candidates:
            chosen = candidates[0]
            return {
                "raw_value": chosen,
                "normalized_value": chosen.title(),
                "confidence": 85.0,
            }
        return None

    @classmethod
    def _extract_net_quantity(cls, text: str) -> Optional[dict]:
        """Extracts net quantity declaration (e.g. 'Net Quantity: 250 g', '500 g', '1 kg', '200 ml')."""
        # 1. Prefer explicit Net Quantity / Net Weight declaration
        explicit_pattern = r'(?:net\s*(?:quantity|qty|wt|weight|content)[\s\.:\-_]*)\s*(\d+(?:\.\d+)?)\s*(kg|g|gm|gms|gram|grams|ml|l|ltr|litre|litres|n|pcs|pieces)\b'
        match = re.search(explicit_pattern, text, re.IGNORECASE)
        if match:
            value, unit = match.groups()
            return {
                "raw_value": match.group(0).strip(),
                "normalized_value": f"{value} {unit.lower()}",
                "unit": unit.lower(),
                "confidence": 95.0,
            }

        # 2. Fallback: search for stand-alone quantity, excluding nutrition table reference lines (e.g. 'per 100g')
        for line in text.split("\n"):
            line_str = line.strip()
            if re.search(r'(per\s*100|serving|nutri|fat|carb|protein|sodium|energy)', line_str, re.IGNORECASE):
                continue
            fallback_match = re.search(r'\b(\d+(?:\.\d+)?)\s*(kg|g|gm|gms|gram|grams|ml|l|ltr|litre|litres|n|pcs|pieces)\b', line_str, re.IGNORECASE)
            if fallback_match:
                value, unit = fallback_match.groups()
                return {
                    "raw_value": fallback_match.group(0).strip(),
                    "normalized_value": f"{value} {unit.lower()}",
                    "unit": unit.lower(),
                    "confidence": 85.0,
                }
        return None

    @classmethod
    def _extract_net_quantity_unit(cls, text: str) -> Optional[dict]:
        net_qty = cls._extract_net_quantity(text)
        if net_qty and net_qty.get("unit"):
            return {
                "raw_value": net_qty["unit"],
                "normalized_value": net_qty["unit"],
                "unit": net_qty["unit"],
                "confidence": 92.0,
            }
        return None

    @classmethod
    def _extract_mrp(cls, text: str) -> Optional[dict]:
        """Extracts Maximum Retail Price including taxes."""
        pattern = r'(?:m\.?r\.?p\.?|max(?:imum)?\s*retail\s*price)[\s\.:\-_]*(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d{1,2})?)(?:\s*(?:incl|inclusive|incl\.)\s*(?:of)?\s*(?:all)?\s*taxes)?'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            price = match.group(1)
            raw = match.group(0).strip()
            return {
                "raw_value": raw,
                "normalized_value": f"₹{price}",
                "unit": "INR",
                "confidence": 90.0,
            }
        # Fallback: price on dot-matrix stamp (e.g. 'AP26283 20.00' or '₹20.00')
        fallback = re.search(r'(?:[A-Z0-9]{5,10}\s+(?:₹\s*)?|₹\s*)(\d{2}\.\d{2})\b', text)
        if fallback:
            return {
                "raw_value": fallback.group(0).strip(),
                "normalized_value": f"₹{fallback.group(1)}",
                "unit": "INR",
                "confidence": 85.0,
            }
        return None

    @classmethod
    def _extract_manufacturer_details(cls, text: str) -> Optional[dict]:
        """Extracts manufacturer/packer/importer name and address."""
        pattern = r'(?:mfd(?:\.|\s+by)?|manufactured\s+by|packed\s+by|marketed\s+by)[\s\.:\-_]+([A-Za-z0-9\s,\.\-&]+?(?:Pvt\.?\s*Ltd\.?|Limited|Ltd\.?|Industrial\s+Area|Plot\s+No|Estate|Road|Nagar|State|India|\b\d{6}\b))'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            raw = match.group(0).strip()
            details = match.group(1).strip()
            if len(details) > 10:
                return {
                    "raw_value": raw,
                    "normalized_value": details,
                    "confidence": 85.0,
                }
        return None

    @classmethod
    def _extract_expiry_date(cls, text: str) -> Optional[dict]:
        """Extracts best before or expiry date."""
        pattern = r'(?:best\s*before|use\s*by|exp(?:iry)?(?:\s*date)?|bbd)[\s\.:\-_]+([A-Za-z0-9\/\.\-\s]{3,20})'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            val = match.group(1).strip()
            # If line is generic reference like "REFER TO BODY", check for actual date stamp below
            if not re.search(r'refer', val, re.IGNORECASE):
                return {
                    "raw_value": match.group(0).strip(),
                    "normalized_value": val,
                    "confidence": 88.0,
                }
        # Fallback: scan for standalone date stamps (e.g. 07/04/27)
        dates = re.findall(r'\b(\d{2}/\d{2}/\d{2,4})\b', text)
        if len(dates) >= 2:
            return {
                "raw_value": dates[1],
                "normalized_value": dates[1],
                "confidence": 85.0,
            }
        elif len(dates) == 1 and not re.search(r'mfg|pkd', text, re.IGNORECASE):
            return {
                "raw_value": dates[0],
                "normalized_value": dates[0],
                "confidence": 80.0,
            }
        return None

    @classmethod
    def _extract_mfg_date(cls, text: str) -> Optional[dict]:
        """Extracts date of manufacture or packing."""
        pattern = r'(?:mfg(?:\s*date)?|manufactured\s*on|pkd|packed(?:\s*on)?)[\s\.:\-_]+([A-Za-z0-9\/\.\-\s]{3,20})'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            val = match.group(1).strip()
            if not re.search(r'refer', val, re.IGNORECASE):
                return {
                    "raw_value": match.group(0).strip(),
                    "normalized_value": val,
                    "confidence": 88.0,
                }
        dates = re.findall(r'\b(\d{2}/\d{2}/\d{2,4})\b', text)
        if dates:
            return {
                "raw_value": dates[0],
                "normalized_value": dates[0],
                "confidence": 85.0,
            }
        return None

    @classmethod
    def _extract_batch_number(cls, text: str) -> Optional[dict]:
        """Extracts batch or lot code."""
        pattern = r'(?:batch\s*(?:no\.?|code|#)?|lot\s*(?:no\.?|#)?|b\.?\s*no\.?)[\s\.:\-_]+([A-Za-z0-9\-_]{3,20})'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            val = match.group(1).strip()
            if not re.search(r'refer', val, re.IGNORECASE):
                return {
                    "raw_value": match.group(0).strip(),
                    "normalized_value": val,
                    "confidence": 85.0,
                }
        # Fallback: batch code format on package (e.g. 'AP26283' or 'BHP26283')
        fallback = re.search(r'\b([A-Z]{1,3}\d{4,8})\b', text)
        if fallback:
            return {
                "raw_value": fallback.group(0).strip(),
                "normalized_value": fallback.group(1).strip(),
                "confidence": 85.0,
            }
        return None

    @classmethod
    def _extract_fssai_license(cls, text: str) -> Optional[dict]:
        """Extracts 14-digit FSSAI license number."""
        pattern = r'(?:fssai(?:\s*lic(?:ense)?(?:\s*no\.?)?)?[\s\.:\-_]*)?\b(1\d{13}|2\d{13})\b'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            lic = match.group(1)
            return {
                "raw_value": match.group(0).strip(),
                "normalized_value": lic,
                "confidence": 95.0,
            }
        return None

    @classmethod
    def _extract_consumer_care(cls, text: str) -> Optional[dict]:
        """Extracts phone number, email address, or customer care statement."""
        email_match = re.search(r'[a-zA-Z0-9_\.\+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-\.]+', text)
        phone_match = re.search(r'(?:toll[\s\-]*free|helpline|care\s*no\.?|phone|tel)[\s\.:\-_]*([+0-9\s\-]{8,15})', text, re.IGNORECASE)
        
        found = []
        if email_match:
            found.append(email_match.group(0))
        if phone_match:
            found.append(phone_match.group(1).strip())
        
        if found:
            return {
                "raw_value": ", ".join(found),
                "normalized_value": ", ".join(found),
                "confidence": 90.0,
            }
        return None

    @classmethod
    def _extract_country_of_origin(cls, text: str) -> Optional[dict]:
        """Extracts Country of Origin."""
        pattern = r'(?:country\s*of\s*origin|made\s*in|product\s*of)[\s\.:\-_]+([A-Za-z\s]+?)(?:[\n,\.]|$)'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            country = match.group(1).strip()
            if 2 < len(country) < 30:
                return {
                    "raw_value": match.group(0).strip(),
                    "normalized_value": country.title(),
                    "confidence": 85.0,
                }
        return None

    @classmethod
    def _extract_veg_symbol(cls, text: str) -> Optional[dict]:
        """Detects vegetarian or non-vegetarian text indicators."""
        if re.search(r'\b(pure\s*veg|100%\s*veg|vegetarian)\b', text, re.IGNORECASE):
            return {
                "raw_value": "Vegetarian Declaration",
                "normalized_value": "Vegetarian",
                "confidence": 85.0,
            }
        elif re.search(r'\b(non[\s\-]*veg(?:etarian)?)\b', text, re.IGNORECASE):
            return {
                "raw_value": "Non-Vegetarian Declaration",
                "normalized_value": "Non-Vegetarian",
                "confidence": 85.0,
            }
        return None

    @classmethod
    def _extract_importer_details(cls, text: str) -> Optional[dict]:
        """Extracts importer details if foreign product."""
        pattern = r'(?:imported\s*(?:and\s*marketed)?\s*by)[\s\.:\-_]+([A-Za-z0-9\s,\.\-&]+)'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return {
                "raw_value": match.group(0).strip(),
                "normalized_value": match.group(1).strip(),
                "confidence": 80.0,
            }
        return None

    @classmethod
    def _extract_storage_instructions(cls, text: str) -> Optional[dict]:
        """Extracts storage conditions."""
        pattern = r'(?:store\s*in\s*a?\s*cool(?:,|and)?\s*dry\s*place|keep\s*refrigerated|store\s*away\s*from\s*sunlight)'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return {
                "raw_value": match.group(0).strip(),
                "normalized_value": match.group(0).strip().title(),
                "confidence": 90.0,
            }
        return None

    @classmethod
    def _extract_nutrition_table(cls, text: str) -> dict[str, Optional[dict]]:
        """
        Extracts nutritional information per 100g/ml.
        STRICT GUARDRAIL (NUT-005): Missing nutrition values remain None.
        Never defaulted to 0.
        """
        nutrition_specs = [
            ("energy_kcal", r'(?:energy|calories)[\s\.:\-_|]*(?:\([a-z]+\))?[\s\.:\-_|]*(\d+(?:\.\d+)?)\s*(?:kcal|cal)?', "kcal"),
            ("protein_g", r'protein[\s\.:\-_|]*(?:\([a-z]+\))?[\s\.:\-_|]*(\d+(?:\.\d+)?)\s*(?:g|gm)?', "g"),
            ("carbohydrate_g", r'(?:carbohydrates?|carb)[\s\.:\-_|]*(?:\([a-z]+\))?[\s\.:\-_|]*(\d+(?:\.\d+)?)\s*(?:g|gm)?', "g"),
            ("total_sugars_g", r'(?:total\s*sugars?|sugars?)[\s\.:\-_|]*(?:\([a-z]+\))?[\s\.:\-_|]*(\d+(?:\.\d+)?)\s*(?:g|gm)?', "g"),
            ("added_sugars_g", r'added\s*sugars?[\s\.:\-_|]*(?:\([a-z]+\))?[\s\.:\-_|]*(\d+(?:\.\d+)?)\s*(?:g|gm)?', "g"),
            ("total_fat_g", r'(?:total\s*fat|fat)[\s\.:\-_|]*(?:\([a-z]+\))?[\s\.:\-_|]*(\d+(?:\.\d+)?)\s*(?:g|gm)?', "g"),
            ("saturated_fat_g", r'(?:saturated\s*fat|sat\s*fat)[\s\.:\-_|]*(?:\([a-z]+\))?[\s\.:\-_|]*(\d+(?:\.\d+)?)\s*(?:g|gm)?', "g"),
            ("trans_fat_g", r'trans\s*fat[\s\.:\-_|]*(?:\([a-z]+\))?[\s\.:\-_|]*(\d+(?:\.\d+)?)\s*(?:g|gm)?', "g"),
            ("sodium_mg", r'sodium[\s\.:\-_|]*(?:\([a-z]+\))?[\s\.:\-_|]*(\d+(?:\.\d+)?)\s*(?:mg)?', "mg"),
            ("dietary_fiber_g", r'(?:dietary\s*fiber|fiber)[\s\.:\-_|]*(?:\([a-z]+\))?[\s\.:\-_|]*(\d+(?:\.\d+)?)\s*(?:g|gm)?', "g"),
        ]

        result = {}
        for key, pattern, default_unit in nutrition_specs:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                val = float(match.group(1))
                result[key] = {
                    "raw_value": match.group(0).strip(),
                    "normalized_value": str(val),
                    "numeric_value": val,
                    "unit": default_unit,
                    "confidence": 88.0,
                }
            else:
                # NUT-005: strictly None if absent
                result[key] = None

        return result

    @classmethod
    def _extract_ingredients_list(cls, text: str) -> list[str]:
        """Extracts ingredients and parses into comma-separated normalized items."""
        pattern = r'(?:ingredients|contains)[\s\.:\-_]+([A-Za-z0-9\s,\.\(\)%-]+?)(?:\n\n|\bmanufactured\b|\bmrp\b|\bfssai\b|\bnet\b|\bnutritional\b|\ballergen\b|$)'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            ing_block = match.group(1).strip()
            # Split by comma or semicolon
            raw_tokens = re.split(r'[,;]\s*', ing_block)
            cleaned = []
            for token in raw_tokens:
                token_clean = re.sub(r'[\(\)\.]', '', token).strip()
                if 2 < len(token_clean) < 40 and not re.search(r'(mfg|exp|batch|fssai)', token_clean, re.IGNORECASE):
                    cleaned.append(token_clean.title())
            return cleaned
        return []

    @classmethod
    def _extract_allergens(cls, text: str, ingredients: list[str]) -> list[str]:
        """Detects declared allergens per FSSAI 2020 schedule."""
        common_allergens = [
            "gluten", "wheat", "peanuts", "tree nuts", "almonds", "cashews",
            "milk", "dairy", "soy", "soybean", "egg", "eggs", "fish", "crustacean", "sesame"
        ]
        found = set()

        # Check explicit allergen advisory block: "Contains: ...", "Allergen advice: ..."
        advisory_match = re.search(r'(?:contains|allergen\s*advi[cs]e)[\s\.:\-_]+([^\.\n]+)', text, re.IGNORECASE)
        if advisory_match:
            block = advisory_match.group(1).lower()
            for allergen in common_allergens:
                if allergen in block:
                    found.add(allergen.title())

        # Also inspect parsed ingredients
        for ing in ingredients:
            ing_lower = ing.lower()
            for allergen in common_allergens:
                if allergen in ing_lower:
                    found.add(allergen.title())

        return sorted(list(found))
