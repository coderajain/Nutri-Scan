#  NutriScan
### AI-Powered Packaged Food Label Analysis, Nutritional Assessment & Legal Metrology Compliance

<p align="center">
  **Scan • Analyze • Understand • Make Informed Choices**
</p>

---

##  About the Project

**NutriScan** is a proposed AI-powered web application designed to analyze packaged food labels, assess nutritional information, and evaluate compliance with the Legal Metrology (Packaged Commodities) Rules, 2011.

The system aims to simplify the process of understanding food packaging by using Optical Character Recognition (OCR), Computer Vision, and rule-based analysis.

Users will be able to upload or capture images of packaged food labels and receive structured information about ingredients, nutritional values, mandatory declarations, and potential compliance issues.

##  Project Objectives

- Automate the extraction of information from packaged food labels.
- Analyze ingredients and nutritional information.
- Evaluate mandatory declarations under applicable Legal Metrology requirements.
- Identify potentially missing or unclear label information.
- Generate explainable compliance and nutritional assessments.
- Maintain a searchable history of product inspections.
- Generate downloadable product analysis reports.

##  Planned Features

| Feature | Description |
|---|---|
|  Smart Label Scanning | Upload or capture packaged food label images. |
|  OCR & Text Extraction | Extract information using Tesseract OCR. |
|  Legal Metrology Checker | Evaluate applicable mandatory packaging declarations. |
|  Nutritional Analysis | Analyze sugar, protein, fat, sodium and other nutritional values. |
|  Ingredient Analysis | Identify selected additives, preservatives and allergens. |
|  Assessment Dashboard | Display compliance and nutritional findings. |
|  Report Generation | Generate detailed product analysis reports. |
|  Scan History | Store and review previous product inspections. |

##  Proposed Technology Stack

### Frontend
- React.js
- Tailwind CSS

### Backend
- Python
- FastAPI
- Uvicorn

### AI & Image Processing
- OpenCV
- Tesseract OCR
- Python-based text processing

### Database
- PostgreSQL

### Security & Deployment
- JWT Authentication
- Docker
- Docker Compose

##  Proposed System Architecture

```text
           USER
             |
             ▼
      React.js Frontend
             |
             ▼
       FastAPI Backend
             |
       ┌─────┴──────┐
       ▼            ▼
  OpenCV        Tesseract OCR
       |            |
       └─────┬──────┘
             ▼
     Information Extraction
             |
       ┌─────┴──────────┐
       ▼                ▼
 Legal Metrology    Nutrition &
   Rule Engine     Ingredient Analysis
       |                |
       └───────┬────────┘
               ▼
        Assessment Engine
               |
               ▼
          PostgreSQL
               |
               ▼
       Dashboard & Reports
```

##  Project Workflow

1. User uploads or captures a packaged food label.
2. The image is processed using OpenCV.
3. Tesseract OCR extracts the visible text.
4. The backend identifies important product declarations.
5. Legal Metrology rules are applied to relevant declarations.
6. Ingredients and nutritional values are analyzed.
7. The system generates separate compliance and nutritional assessments.
8. Results are displayed on the dashboard and stored for future reference.

##  Future Enhancements

- Product authenticity and counterfeit-risk detection.
- Barcode-based product information lookup.
- AI-assisted food label explanation.
- Smart product comparison.
- Hindi and regional language support.
- Manufacturer and product traceability integrations.

*These are proposed enhancements and are not currently implemented.*

##  Project Status

**Currently: Planning & Initial Development Setup**

NutriScan is being developed as an academic project. The architecture, requirements and technology stack have been documented. Implementation and testing will proceed in planned phases.

##  Developer

**Aashay Jain**

Bachelor of Technology – Computer Science & Engineering

Medicaps University, Indore

##  Project Information

- Project Name: NutriScan
- Project Type: Academic Software Development Project
- Version: 1.0 (Planned)
- Repository: [Nutri-Scan](https://github.com/coderajain/Nutri-Scan)

---

<p align="center">
  **NutriScan – Making Food Labels Easier to Understand.** 🥗
</p>
