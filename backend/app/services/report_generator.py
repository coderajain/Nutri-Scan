"""ReportLab PDF compliance and nutrition report generator (REP-001, REP-002, REP-004, SAF-001, SAF-002)."""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import logging

logger = logging.getLogger("nutriscan.services.report_generator")


class PDFReportGenerator:
    """Generates official academic / evaluation PDF audit reports for packaged commodity scans."""

    @classmethod
    def generate_pdf(
        cls,
        scan_id: str,
        product_name: str,
        rule_version_tag: str,
        compliance_score: float,
        nutrition_score: float | None,
        compliance_status: str,
        nutrition_status: str,
        findings: list[dict],
        original_image_path: str,
        output_pdf_path: str,
        created_at_str: str,
    ) -> str:
        """Assembles a publication-ready multi-section PDF document."""
        os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)

        doc = SimpleDocTemplate(
            output_pdf_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()
        
        # Custom Typography
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#1e293b"),
            spaceAfter=4,
        )
        subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#64748b"),
        )
        section_style = ParagraphStyle(
            "SectionHeader",
            parent=styles["Heading2"],
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#0f172a"),
            spaceBefore=12,
            spaceAfter=6,
        )
        body_style = ParagraphStyle(
            "BodySmall",
            parent=styles["Normal"],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#334155"),
        )
        disclaimer_style = ParagraphStyle(
            "Disclaimer",
            parent=styles["Normal"],
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#64748b"),
        )

        elements = []

        # 1. Header Banner
        elements.append(Paragraph("<b>NutriScan v1.0</b> — Packaging Compliance & Nutritional Audit", title_style))
        elements.append(Paragraph(
            "Department of Computer Science & Engineering | Medi-Caps University, Indore<br/>"
            f"<b>Scan Reference ID:</b> {scan_id} &nbsp;|&nbsp; <b>Timestamp:</b> {created_at_str} &nbsp;|&nbsp; <b>Rule Version:</b> {rule_version_tag}",
            subtitle_style
        ))
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563eb"), spaceAfter=12))

        # 2. Executive Summary & Scores Grid
        comp_color = "#16a34a" if compliance_score >= 90 else ("#d97706" if compliance_score >= 60 else "#dc2626")
        nutri_score_str = f"{nutrition_score} / 100" if nutrition_score is not None else "Insufficient Data"
        nutri_color = "#16a34a" if (nutrition_score or 0) >= 65 else "#d97706"

        summary_data = [
            [
                Paragraph("<b>Product Identified:</b>", body_style),
                Paragraph(product_name or "Packaged Commodity (Unlabeled)", body_style),
                Paragraph("<b>Audit Status:</b>", body_style),
                Paragraph(f"<b>{compliance_status.upper()}</b>", body_style),
            ],
            [
                Paragraph("<b>Legal Metrology Score:</b>", body_style),
                Paragraph(f"<font color='{comp_color}'><b>{compliance_score} / 100</b></font>", body_style),
                Paragraph("<b>Nutritional Score:</b>", body_style),
                Paragraph(f"<font color='{nutri_color}'><b>{nutri_score_str}</b></font>", body_style),
            ],
        ]
        summary_table = Table(summary_data, colWidths=[1.8 * inch, 2.0 * inch, 1.8 * inch, 1.8 * inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 12))

        # 3. Label Evidence Image (if accessible)
        if os.path.exists(original_image_path):
            try:
                elements.append(Paragraph("<b>Preserved Physical Label Evidence (SCAN-003)</b>", section_style))
                # Auto-scale image to fit 3.5 inches height
                img_flow = RLImage(original_image_path, width=4.5 * inch, height=2.8 * inch)
                elements.append(img_flow)
                elements.append(Spacer(1, 8))
            except Exception as e:
                logger.warning(f"Could not render image inside PDF: {e}")

        # 4. Granular Findings Table (LM-004)
        elements.append(Paragraph("<b>Detailed Regulatory & Nutritional Findings</b>", section_style))
        
        table_rows = [
            [
                Paragraph("<b>Requirement / Declaration</b>", body_style),
                Paragraph("<b>Status</b>", body_style),
                Paragraph("<b>Observed Evidence</b>", body_style),
                Paragraph("<b>Condition / Legal Rule</b>", body_style),
            ]
        ]

        for f in findings[:25]:  # include up to 25 primary findings
            ftype = str(f.get("finding_type", "")).upper()
            status_color = "#16a34a" if ftype == "PASS" else ("#dc2626" if ftype == "FAIL" else "#d97706")
            
            table_rows.append([
                Paragraph(f.get("title", ""), body_style),
                Paragraph(f"<font color='{status_color}'><b>{ftype}</b></font>", body_style),
                Paragraph(f.get("observed_value") or "Not Found", body_style),
                Paragraph(f.get("expected_condition") or f.get("message", ""), body_style),
            ])

        findings_table = Table(table_rows, colWidths=[2.2 * inch, 1.0 * inch, 2.0 * inch, 2.2 * inch])
        findings_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('PADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(findings_table)
        elements.append(Spacer(1, 14))

        # 5. Statutory & Medical Disclaimers (SAF-001, SAF-002, LM-005)
        disclaimer_box = [
            [
                Paragraph(
                    "<b>REGULATORY AND MEDICAL DISCLAIMER NOTICE:</b><br/>"
                    "1. <b>Automated Decision Support Screening (SAF-001):</b> This document is an automated screening aid developed for academic research (B.Tech CSE Project-1, Medi-Caps University). It does NOT constitute a statutory or legally binding certification of compliance under the Legal Metrology Act, 2009 or FSSAI Regulations.<br/>"
                    "2. <b>Informational Nutritional Assessment (SAF-002):</b> Nutritional scores and alerts are computed from visible label declarations and general dietary guidelines. They do NOT constitute medical diagnosis, treatment, or personalized clinical nutrition advice.<br/>"
                    "3. <b>Physical Scale Heuristics (LM-005):</b> Physical packaging dimensions, such as printed font heights, cannot be conclusively certified from digital photographs without physical calibration scale references and require manual verification.",
                    disclaimer_style,
                )
            ]
        ]
        disclaimer_table = Table(disclaimer_box, colWidths=[7.4 * inch])
        disclaimer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#fef2f2")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#f87171")),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(KeepTogether(disclaimer_table))

        # Build Document
        doc.build(elements)
        logger.info(f"ReportLab PDF report generated successfully: {output_pdf_path}")
        return output_pdf_path
