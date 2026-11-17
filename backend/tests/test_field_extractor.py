"""Unit tests for FieldExtractor (OCR-004, OCR-005, OCR-007, NUT-005)."""
from app.services.field_extractor import FieldExtractor

SAMPLE_OCR_TEXT = """
HEALTHY HARVEST WHOLE WHEAT BISCUITS
Ingredients: Whole Wheat Flour (62%), Sugar, Edible Vegetable Oil (Palm Oil), Invert Sugar Syrup, Leavening Agents (INS 500ii, INS 503ii), Emulsifier (INS 322), Iodised Salt.
Contains: Wheat, Soy. May contain traces of Nuts and Milk.
Nutritional Information per 100g:
Energy 450 kcal
Protein 7.8 g
Carbohydrate 68 g
Total Sugars 18.5 g
Added Sugars 16.0 g
Total Fat 16.2 g
Saturated Fat 7.5 g
Trans Fat 0.1 g
Sodium 380 mg
Net Quantity: 250 g
MRP: ₹ 45.00 (Inclusive of all taxes)
Mfg Date: 15/10/2026
Best Before 6 Months from Packaging
Batch No: B26-1049
FSSAI Lic. No. 10018022007890
Customer Care: 1800-200-8899, care@healthyharvest.in
Manufactured by: Healthy Harvest Foods Ltd., Plot 42, Sector 5, Pithampur Industrial Area, Dhar, MP 454775
Country of Origin: India
100% Pure Veg
Store in a cool and dry place away from sunlight.
"""


def test_field_extraction_declarations():
    """Tests extraction of mandatory packaged commodity declarations."""
    extracted = FieldExtractor.extract_all(SAMPLE_OCR_TEXT)
    declarations = extracted["declarations"]

    assert declarations["net_quantity"] is not None
    assert declarations["net_quantity"]["normalized_value"] == "250 g"
    assert declarations["net_quantity_unit"]["normalized_value"] == "g"

    assert declarations["mrp"] is not None
    assert declarations["mrp"]["normalized_value"] == "₹45.00"

    assert declarations["fssai_license"] is not None
    assert declarations["fssai_license"]["normalized_value"] == "10018022007890"

    assert declarations["expiry_date"] is not None
    assert "6 Months" in declarations["expiry_date"]["normalized_value"]

    assert declarations["batch_number"] is not None
    assert declarations["batch_number"]["normalized_value"] == "B26-1049"

    assert declarations["country_of_origin"] is not None
    assert declarations["country_of_origin"]["normalized_value"] == "India"


def test_field_extraction_nutrition_table():
    """Tests nutritional table parsing and verifies zero-fabrication (NUT-005)."""
    extracted = FieldExtractor.extract_all(SAMPLE_OCR_TEXT)
    nutrition = extracted["nutrition"]

    assert nutrition["energy_kcal"]["numeric_value"] == 450.0
    assert nutrition["protein_g"]["numeric_value"] == 7.8
    assert nutrition["carbohydrate_g"]["numeric_value"] == 68.0
    assert nutrition["total_sugars_g"]["numeric_value"] == 18.5
    assert nutrition["added_sugars_g"]["numeric_value"] == 16.0
    assert nutrition["saturated_fat_g"]["numeric_value"] == 7.5
    assert nutrition["sodium_mg"]["numeric_value"] == 380.0

    # Dietary fiber was absent in sample OCR text -> MUST BE None, NEVER defaulted to 0
    assert nutrition["dietary_fiber_g"] is None


def test_zero_fabrication_on_empty_text():
    """Strictly verifies that missing label evidence yields None/empty structures (OCR-007, SAF-003)."""
    empty_result = FieldExtractor.extract_all("")
    for key, val in empty_result["declarations"].items():
        assert val is None

    for key, val in empty_result["nutrition"].items():
        assert val is None

    assert empty_result["ingredients"] == []
    assert empty_result["allergens"] == []
