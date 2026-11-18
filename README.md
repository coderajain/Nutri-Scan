# NutriScan v1.0
### An AI-Assisted System for Packaged Food Label Analysis, Nutritional Assessment, and Legal Metrology Compliance

---

## 1. Executive Summary & Architecture Overview

NutriScan is a full-stack, AI-assisted decision-support platform designed to automate the screening and verification of packaged food product labels in India. It addresses the labor-intensive inspection required under the **Legal Metrology Act, 2009**, the **Legal Metrology (Packaged Commodities) Rules, 2011 (LM-PC Rules)**, and the **Food Safety and Standards Authority of India (FSSAI) Labelling and Display Regulations, 2020**.

### Core Architecture & Processing Pipeline

```
[1. Label Image Capture / Upload]
               │
               ▼ (SCAN-003: Evidence preserved in isolated volume)
[2. OpenCV Image Enhancement Pipeline]
   ├── Bicubic High-DPI Rescaling
   ├── Grayscale & Contrast Enhancement (CLAHE)
   ├── Bilateral Noise Denoising with Edge Preservation
   ├── Deskewing & Orientation Correction (minAreaRect)
   └── Adaptive Otsu Binarization
               │
               ▼
[3. Tesseract 5.x OCR Engine] (OCR-001, OCR-003)
   ├── LSTM Neural Net Engine (--oem 1 --psm 3)
   └── Word-Level Confidence Extraction & Layout Mapping
               │
               ▼
[4. Structured Field Extractor] (OCR-004, OCR-005, OCR-007)
   ├── Mandatory Declarations (Net Qty, MRP, Mfg/Exp Date, FSSAI, Consumer Care)
   ├── Ingredients Tokenizer & Additives Classifier (INS Database)
   └── Nutrition Facts Table Parser (per 100g/ml; zero-fabrication strictly enforced)
               │
         ┌─────┴────────────────────────────────┐
         ▼                                      ▼
[5. Legal Metrology Engine]           [6. Nutrition Assessment Engine]
   (LM-001 to LM-007)                    (NUT-001 to NUT-006, SAF-002)
   ├── 20 Versioned Statutory Rules       ├── Sugar, Saturated Fat, Sodium Limits
   ├── LM-PC-2011 v1.0 Ruleset            ├── Trans Fat Zero-Tolerance Check
   └── Font Height Manual Review Flag     └── Ultra-processed Additive Detection
         │                                      │
         └─────┬────────────────────────────────┘
               ▼
[7. Independent Scoring Engine] (SCORE-001, SCORE-002: Separated Scores)
   ├── Legal Metrology Compliance Score (0.0% – 100.0%)
   └── Nutritional Profile Health Score (0 – 100 / Insufficient Data)
               │
               ▼
[8. ReportLab PDF Audit Generator & Persistence] (REP-001, REP-004, HIS-001)
   ├── Original Evidence Image Embed + Detailed Findings Grid
   └── Mandatory Statutory & Medical Disclaimers
```

---

## 2. Technology Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Frontend** | React 18 (Vite), Tailwind CSS 3.4, Lucide Icons, Axios, React Router 6 |
| **Backend API** | Python 3.11+, FastAPI 0.111, Uvicorn, Pydantic v2 Settings |
| **Database & ORM** | PostgreSQL 16+ / SQLite (fallback), SQLAlchemy 2.0, Alembic 1.13 |
| **CV & OCR Pipeline** | OpenCV Headless 4.9, Tesseract OCR 5.x, PyTesseract 0.3.10, NumPy 1.26 |
| **PDF Reporting** | ReportLab 4.1 (Clean typographic tables, evidence image flowables) |
| **Security & Auth** | Passlib (bcrypt salted hashing), Python-Jose (expiring JWT tokens) |
| **DevOps & Containers** | Docker & Docker Compose v3.8 (`frontend`, `backend`, `db` + volumes) |

---

## 3. Strict Architectural & Safety Guardrails (SRS Compliance)

1. **Zero Fabrication (`OCR-007`, `SAF-003`, `NUT-005`):**  
   The system never fabricates, hallucinates, or defaults missing label declarations or nutrient amounts to zero. If an attribute or nutrient value is absent from the OCR output, it is stored as `null` and flagged as `Not Found` or `Uncertain`.
2. **Separation of Scores (`SCORE-001`, `SCORE-002`):**  
   The **Legal Metrology Compliance Score** and the **Nutritional Profile Score** are computed independently and presented side-by-side without merging. An ultra-processed snack can achieve 100% packaging compliance while receiving a high-risk nutritional rating.
3. **Traceable Versioned Rules (`LM-001`, `LM-006`, `HIS-003`):**  
   Rules are stored in PostgreSQL under explicit version tags (e.g., `LM-PC-2011-v1.0`). Any administrative update or rule modification spawns a new version so historical scans remain permanently linked to the exact statutory version active when they were inspected.
4. **Non-Authoritative Disclaimers (`LM-005`, `LM-007`, `SAF-001`, `SAF-002`):**  
   - Compliance outputs are classified as *automated decision-support screening*, not a statutory certification under the Legal Metrology Act, 2009.
   - Nutritional profile scores are classified as *informational dietary indicators*, not medical diagnosis or clinical treatment.
   - Physical package properties (such as numeral font height in millimeters) are flagged for `Manual Review` (`LM-005`) because digital camera photographs lack physical millimeter calibration references.
5. **Evidence Preservation (`SCAN-003`, `SEC-006`):**  
   Original uploaded images are saved in an isolated storage directory (`data/evidence/`) outside executable code directories. Downstream OCR or PDF exceptions never delete or overwrite preserved evidence.
6. **Security Hardening (`SEC-001` to `SEC-011`):**  
   Bcrypt salted password hashing, expiring JWT bearer tokens, role-based access control (`Standard User` vs `Administrator`), parameterized ORM queries, and sanitized error messages that never leak database schemas, stack traces, or internal file paths.

---

## 4. Legal Metrology (LM-PC Rules, 2011) Statutory Coverage

NutriScan v1.0 seeds 20 statutory rules under the `LM-PC-2011-v1.0` ruleset:

| Rule Code | Mandatory Declaration | Statutory Legal Reference | Severity |
| :--- | :--- | :--- | :--- |
| `LM-R-001` | Net Quantity Declaration | Rule 6(1)(e), LM-PC Rules, 2011 | **CRITICAL** |
| `LM-R-002` | Standard Metric Units (g, kg, ml, l) | Rule 12 & Schedule II, LM-PC Rules | **CRITICAL** |
| `LM-R-003` | Manufacturer / Packer Name & Address | Rule 6(1)(a), LM-PC Rules, 2011 | **CRITICAL** |
| `LM-R-004` | Best Before / Expiry Date | Rule 6(1)(d), LM-PC Rules & FSSAI 2020 | **CRITICAL** |
| `LM-R-005` | Month & Year of Manufacture / Packing | Rule 6(1)(d), LM-PC Rules, 2011 | **MAJOR** |
| `LM-R-006` | MRP inclusive of all taxes (₹ symbol) | Rule 6(1)(e), LM-PC Rules, 2011 | **CRITICAL** |
| `LM-R-007` | Consumer Care Executive Details | Rule 6(1)(n), LM-PC Rules, 2011 | **MAJOR** |
| `LM-R-008` | Country of Origin Declaration | Rule 6(1)(f), LM-PC Rules, 2011 | **MAJOR** |
| `LM-R-009` | Batch / Lot / Identification Code | Rule 6(1)(g), LM-PC Rules, 2011 | **MAJOR** |
| `LM-R-010` | 14-Digit FSSAI License Number | FSSAI Labelling Regulations 2020 | **CRITICAL** |
| `LM-R-011` | Common / Generic Commodity Name | Rule 6(1)(b), LM-PC Rules, 2011 | **CRITICAL** |
| `LM-R-012` | Descending Order Ingredients List | FSSAI Regulations 2020, Reg 5(1) | **MAJOR** |
| `LM-R-013` | Nutritional Facts Panel per 100g/ml | FSSAI Regulations 2020, Reg 5(2) | **MAJOR** |
| `LM-R-014` | Added Sugars & Saturated Fat Breakup | FSSAI Labelling Regulations 2020 | **MAJOR** |
| `LM-R-015` | Sodium Content Declaration (mg) | FSSAI Regulations 2020, Reg 5(2)(iv) | **MAJOR** |
| `LM-R-016` | Allergen Declaration / Advisory | FSSAI Schedule on Specified Allergens | **CRITICAL** |
| `LM-R-017` | Vegetarian / Non-Vegetarian Symbol | FSSAI Regulations 2020, Reg 5(4) | **MAJOR** |
| `LM-R-018` | Min. Font Height for Net Quantity | Rule 7 & Table II, LM-PC Rules [Manual Review] | **RECOMMENDED** |
| `LM-R-019` | Importer Name & Complete Address | Rule 6(1)(aa), LM-PC Rules, 2011 | **MAJOR** |
| `LM-R-020` | Storage Instructions & Recommendations | FSSAI Regulations 2020, Reg 5(7) | **RECOMMENDED** |

---

## 5. Software Requirements Specification (SRS) Compliance Matrix

| SRS Req ID | Requirement Description | Implementation Component | Status |
| :--- | :--- | :--- | :--- |
| `AUTH-001` | User login with valid credentials | `backend/app/api/auth.py` | **VERIFIED** |
| `AUTH-002` | Reject invalid credentials with generic error | `backend/app/api/auth.py` | **VERIFIED** |
| `AUTH-003` | Enforce server-side role authorization | `backend/app/api/deps.py` (`require_admin`) | **VERIFIED** |
| `AUTH-004` | Support Standard User & Admin roles | `backend/app/models/user.py` (`UserRole`) | **VERIFIED** |
| `AUTH-005` | Expiring JWT access tokens | `backend/app/core/security.py` | **VERIFIED** |
| `AUTH-006` | Security audit log for administrative actions | `backend/app/models/audit_log.py` | **VERIFIED** |
| `SCAN-001` | Accept JPG, JPEG, PNG, WEBP images | `backend/app/api/scans.py` | **VERIFIED** |
| `SCAN-002` | Reject unsupported or oversized (>15MB) files | `backend/app/api/scans.py` | **VERIFIED** |
| `SCAN-003` | Preserve original evidence in isolated volume | `backend/app/api/scans.py` (`data/evidence/`) | **VERIFIED** |
| `SCAN-004` | OpenCV image preprocessing & deskewing | `backend/app/services/image_processor.py` | **VERIFIED** |
| `OCR-001` | Invoke Tesseract OCR on processed image | `backend/app/services/ocr_engine.py` | **VERIFIED** |
| `OCR-003` | Capture word-level OCR confidence | `backend/app/services/ocr_engine.py` | **VERIFIED** |
| `OCR-004` | Normalize OCR variations and currency symbols | `backend/app/services/field_extractor.py` | **VERIFIED** |
| `OCR-005` | Extract structured declarations and nutrition | `backend/app/services/field_extractor.py` | **VERIFIED** |
| `OCR-007` | Zero fabrication of absent values | `backend/app/services/field_extractor.py` | **VERIFIED** |
| `LM-001` | Identify rule version tag on every evaluation | `backend/app/models/scan.py` (`rule_version_id`)| **VERIFIED** |
| `LM-003` | Findings as Pass, Fail, Not Found, Manual Review| `backend/app/services/compliance_engine.py` | **VERIFIED** |
| `LM-004` | Finding shows observed value and statutory rule | `backend/app/services/compliance_engine.py` | **VERIFIED** |
| `LM-005` | Font height heuristic marked non-authoritative | `backend/app/services/compliance_engine.py` | **VERIFIED** |
| `LM-006` | Versioned rules do not alter historical scans | `backend/app/models/rule_version.py` | **VERIFIED** |
| `NUT-001` | Extract energy, protein, carb, fat, sodium | `backend/app/services/field_extractor.py` | **VERIFIED** |
| `NUT-004` | Detect additives, preservatives, INS numbers | `backend/app/services/nutrition_engine.py` | **VERIFIED** |
| `NUT-005` | Missing nutrition values remain null (not zero) | `backend/app/services/field_extractor.py` | **VERIFIED** |
| `NUT-006` | Informational findings, not medical diagnosis | `backend/app/services/nutrition_engine.py` | **VERIFIED** |
| `SCORE-001`| Calculate Legal Metrology Compliance Score | `backend/app/services/scoring_engine.py` | **VERIFIED** |
| `SCORE-002`| Calculate Nutritional Profile Score | `backend/app/services/scoring_engine.py` | **VERIFIED** |
| `SCORE-004`| Flag insufficient data when <3 nutrients present| `backend/app/services/scoring_engine.py` | **VERIFIED** |
| `REP-001` | Generate audit report with findings & evidence | `backend/app/services/report_generator.py` | **VERIFIED** |
| `REP-004` | Downloadable ReportLab PDF export | `backend/app/services/report_generator.py` | **VERIFIED** |
| `HIS-001` | Store scan timestamp, user, fields, scores | `backend/app/models/scan.py` | **VERIFIED** |
| `HIS-004` | Paginated scan history repository | `backend/app/api/history.py` | **VERIFIED** |
| `DASH-001` | Dashboard scan aggregates and recent activity | `backend/app/api/dashboard.py` | **VERIFIED** |
| `SEC-001` | Bcrypt salted password hashing | `backend/app/core/security.py` | **VERIFIED** |
| `SEC-011` | Error responses never expose stack traces/paths | `backend/app/core/exceptions.py` | **VERIFIED** |

---

## 6. Docker & Local Deployment Guide

### Prerequisites
- Docker Engine 24+ & Docker Compose v2.20+ (Or Python 3.11+ and Node 20+ for native host execution)

### 1. Clone & Configure Environment Variables
```bash
git clone https://github.com/coderajain/Nutri-Scan.git
cd Nutri-Scan

# Copy environment configuration
cp .env.example .env
```

### 2. Launch Services

#### Option A: One-Click Local Launch (Windows)
Double-click `start.bat` or run in PowerShell:
```powershell
.\start.ps1
```
This automatically starts both the FastAPI backend and React frontend in separate titled console windows. To stop both services, run `stop.bat`.

#### Option B: Launch with Docker Compose
```bash
docker-compose up --build -d
```

### 3. Verify Running Services
```bash
docker-compose ps
```
The three containers will start:
- **`nutriscan_frontend`**: React + Vite UI at `http://localhost:3000`
- **`nutriscan_backend`**: FastAPI REST API at `http://localhost:8000` (Swagger UI at `/docs`)
- **`nutriscan_db`**: PostgreSQL 16 container at `localhost:5432`

---

## 7. Default Demo & Evaluator Credentials

On initial database boot, the seed runner automatically provisions two accounts:

| User Class | Email Address | Default Password | Role Privileges |
| :--- | :--- | :--- | :--- |
| **Administrator / Project Lead** | `admin@nutriscan.local` | `AdminPassword@2026!` | Full Admin, Rule Versioning, Audit Logs |
| **Academic Evaluator / Demo** | `demo@nutriscan.local` | `DemoPassword@2026!` | Standard User, Scans, Reports, History |

*Fast Login shortcuts are also provided on the web login screen for viva demonstration.*

---

## 8. Running the Backend Test Suite

To verify OCR extraction accuracy, zero-fabrication constraints, and score separation:

```bash
cd backend
pytest tests/ -v
```

Expected output:
```
tests/test_field_extractor.py::test_field_extraction_declarations PASSED
tests/test_field_extractor.py::test_field_extraction_nutrition_table PASSED
tests/test_field_extractor.py::test_zero_fabrication_on_empty_text PASSED
tests/test_scoring_engine.py::test_separation_of_scores PASSED
tests/test_scoring_engine.py::test_insufficient_nutrition_data PASSED
========================= 5 passed in 0.42s =========================
```

---

## 9. Academic & Regulatory Disclaimer Notice

> **IMPORTANT REGULATORY AND MEDICAL NOTICE:**  
> 1. **Automated Screening Tool (`SAF-001`, `LM-007`):** NutriScan v1.0 is developed as an automated screening tool. It provides automated decision-support screening and does NOT constitute a statutory or legally binding certification of compliance under the Legal Metrology Act, 2009 or FSSAI Regulations.  
> 2. **Informational Nutritional Assessment (`SAF-002`):** Nutritional metrics, additive warnings, and health profile scores represent informational estimates derived from label declarations and general dietary guidelines. They do NOT constitute medical diagnosis, clinical treatment, or personalized clinical nutrition advice.  
> 3. **Physical Scale Heuristics (`LM-005`):** Physical package properties (e.g. printed font height in millimeters per Table II of LM-PC Rules 2011) cannot be certified conclusively from digital images without physical scale calibration references and require manual verification.
