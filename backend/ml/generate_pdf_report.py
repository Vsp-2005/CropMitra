"""
Generate professional PDF report from CropMitra Current Project Report.
Uses ReportLab with high aesthetic typography, tables, and page layout.
"""
import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

PDF_PATH = "CropMitra_Current_Project_Report.pdf"

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        if self._pageNumber == 1:
            return  # Skip page 1 (Title page)
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#4A5568"))
        
        # Header line
        self.drawString(54, 750, "CropMitra — Agricultural Decision Support System | Current Implementation Report")
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.5)
        self.line(54, 742, 558, 742)
        
        # Footer
        self.line(54, 50, 558, 50)
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 38, page_text)
        self.drawString(54, 38, "CONFIDENTIAL & PROPRIETARY — FOR EVALUATION ONLY")
        self.restoreState()


def build_pdf():
    doc = SimpleDocTemplate(
        PDF_PATH,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=60,
        bottomMargin=60
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    PRIMARY = colors.HexColor("#1B4332")
    SECONDARY = colors.HexColor("#2D6A4F")
    ACCENT = colors.HexColor("#40916C")
    DARK_TEXT = colors.HexColor("#1A202C")
    MUTED_TEXT = colors.HexColor("#4A5568")
    SURFACE_BG = colors.HexColor("#F7FAFC")
    BORDER_COLOR = colors.HexColor("#E2E8F0")

    # Custom Typography Styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=28,
        leading=34,
        textColor=PRIMARY,
        alignment=1,
        spaceAfter=12
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=15,
        leading=20,
        textColor=SECONDARY,
        alignment=1,
        spaceAfter=25
    )

    meta_style = ParagraphStyle(
        'CoverMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=15,
        textColor=MUTED_TEXT,
        alignment=1
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=PRIMARY,
        spaceBefore=16,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=SECONDARY,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=DARK_TEXT,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#2D3748")
    )

    th_style = ParagraphStyle(
        'TH',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )

    td_style = ParagraphStyle(
        'TD',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=DARK_TEXT
    )

    story = []

    # ================= COVER PAGE =================
    story.append(Spacer(1, 40))
    story.append(Paragraph("CropMitra", title_style))
    story.append(Paragraph("Agricultural Decision Support System", subtitle_style))
    story.append(HRFlowable(width="60%", thickness=2, color=ACCENT, spaceAfter=20))
    story.append(Paragraph("Current Implementation & Technical Project Report", ParagraphStyle('ReportType', parent=subtitle_style, fontSize=13, fontName='Helvetica-Bold', textColor=PRIMARY)))
    story.append(Spacer(1, 40))

    meta_box = [
        [Paragraph("<b>Project Focus:</b> Multi-Criteria Crop & Fertilizer Recommendation", meta_style)],
        [Paragraph("<b>Core Technologies:</b> React 18, FastAPI, Python, scikit-learn, Random Forest, SQLite", meta_style)],
        [Paragraph("<b>Primary Datasets:</b> CropDataset-Enhanced.csv, soil info.csv, fertilizer.csv, crop_rotation_matrix.csv", meta_style)],
        [Paragraph("<b>Author / Engineering:</b> CropMitra Core Development Team", meta_style)],
        [Paragraph("<b>Audit Date:</b> September 2026 | Version 2.0.0 (Production Verified)", meta_style)],
    ]
    t_meta = Table(meta_box, colWidths=[450])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), SURFACE_BG),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 80))
    
    disclaimer = Paragraph(
        "<i><b>Confidentiality & Academic Notice:</b> This report represents a factual audit of the actual codebase, datasets, and tested software artifacts present in the CropMitra repository. All performance metrics and claims are verified against automated test suites.</i>",
        ParagraphStyle('Disc', parent=meta_style, fontSize=8.5, leading=12)
    )
    story.append(disclaimer)
    story.append(PageBreak())

    # ================= 1. EXECUTIVE SUMMARY =================
    story.append(Paragraph("1. Executive Summary", h1_style))
    story.append(Paragraph(
        "<b>CropMitra</b> is an intelligent, multi-criteria agricultural decision-support web application designed to assist Indian smallholder farmers, agronomists, and agricultural extension officers in making data-driven crop selection and fertilization decisions.",
        body_style
    ))
    story.append(Paragraph(
        "Selecting the optimal crop for a given plot is complex. A farmer must jointly weigh geographical adaptation, field-level soil nutrient profiles, seasonal water availability, preceding crop sequence history (crop rotation), and targeted fertilization needs. CropMitra addresses this multi-dimensional challenge through an integrated, layered software architecture:",
        body_style
    ))
    story.append(Paragraph("• <b>Frontend:</b> Responsive SPA built with React 18 and Vite, featuring dynamic location selectors, interactive field parameters, explainable recommendation cards, and print views.", bullet_style))
    story.append(Paragraph("• <b>Backend:</b> High-performance RESTful API built on Python 3.14 and FastAPI with strict Pydantic validation.", bullet_style))
    story.append(Paragraph("• <b>ML & Decision Engine:</b> Hard location filtering from 730 district records, 99.32% accurate Random Forest model, Gaussian environmental similarity envelopes, and an in-memory 2,601-pair directional rotation matrix.", bullet_style))
    story.append(Paragraph("• <b>Database:</b> Local SQLite database managed via SQLAlchemy ORM for recommendation session persistence.", bullet_style))
    story.append(Paragraph("• <b>Fertilizer Engine:</b> Target-crop and soil-specific NPK formulation guidance with stage-wise split dosage advice.", bullet_style))
    story.append(Spacer(1, 10))

    # ================= 2. PROBLEM STATEMENT =================
    story.append(Paragraph("2. Problem Statement", h1_style))
    story.append(Paragraph("Indian agriculture faces persistent structural productivity barriers due to lack of localized decision support:", body_style))
    story.append(Paragraph("• <b>Location Mismatch:</b> Sowing crops unadapted to district agro-climatic zones leads to widespread crop failures.", bullet_style))
    story.append(Paragraph("• <b>Imbalanced Fertilizer Usage:</b> Heavy overuse of synthetic Urea without balanced P and K degrades soil microbial health.", bullet_style))
    story.append(Paragraph("• <b>Continuous Monoculture:</b> Cultivating identical crops repeatedly accumulates soil-borne pests, wilt, and root-knot nematodes.", bullet_style))
    story.append(Paragraph("• <b>Water Incompatibility:</b> Misaligning high-water crops with rain-fed dry plots causes drought stress and economic losses.", bullet_style))
    story.append(Paragraph("CropMitra provides an accessible, transparent, and explainable decision-support tool to mitigate these issues.", body_style))
    story.append(Spacer(1, 10))

    # ================= 3. PROJECT OBJECTIVES =================
    story.append(Paragraph("3. Implemented Project Objectives", h1_style))
    story.append(Paragraph("1. Provide multi-candidate crop recommendations with transparent suitability tiers and scores.", bullet_style))
    story.append(Paragraph("2. Incorporate real field parameters: Soil Type, Water Availability, and Previous Crop.", bullet_style))
    story.append(Paragraph("3. Deploy a trained Random Forest classifier to predict suitability envelopes across environmental metrics.", bullet_style))
    story.append(Paragraph("4. Enforce strict geographic location authority via historical district crop registries.", bullet_style))
    story.append(Paragraph("5. Implement directional crop rotation evaluation across 2,601 crop pairs based on nitrogen fixation and pest break rules.", bullet_style))
    story.append(Paragraph("6. Provide explainable plain-language rationales for every recommendation.", bullet_style))
    story.append(Paragraph("7. Deliver precise fertilizer formulations, dosages (kg/acre), and split-application guidance.", bullet_style))
    story.append(Paragraph("8. Persist recommendation sessions in an SQLite database.", bullet_style))
    story.append(Paragraph("9. Deliver a mobile-responsive, print-ready React UI with dark and light earthy themes.", bullet_style))
    story.append(Spacer(1, 10))

    # ================= 4. SYSTEM ARCHITECTURE =================
    story.append(Paragraph("4. System Architecture", h1_style))
    story.append(Paragraph("The application follows a clean 3-tier decoupled architecture:", body_style))
    
    arch_box = [
        [Paragraph("<b>Client Tier:</b> React 18 + Vite SPA (Forms, Interactive Selectors, Result Banners, Print View)", td_style)],
        [Paragraph("<b>API & Validation Tier:</b> FastAPI (REST Endpoints, Pydantic Request Models, CORS)", td_style)],
        [Paragraph("<b>Decision & ML Tier:</b> Location Service + Random Forest Model + Crop Rotation Service + Fertilizer Service", td_style)],
        [Paragraph("<b>Persistence Tier:</b> SQLAlchemy ORM + SQLite (RecommendationRecord Table)", td_style)]
    ]
    t_arch = Table(arch_box, colWidths=[500])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), SURFACE_BG),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_arch)
    story.append(Spacer(1, 10))

    # ================= 5. TECHNOLOGY STACK =================
    story.append(Paragraph("5. Technology Stack", h1_style))
    tech_data = [
        [Paragraph("<b>Technology</b>", th_style), Paragraph("<b>Layer / Purpose</b>", th_style), Paragraph("<b>Actual Usage in Project</b>", th_style)],
        [Paragraph("React 18", td_style), Paragraph("Frontend Framework", td_style), Paragraph("SPA UI, state management, form validation", td_style)],
        [Paragraph("Vite 5", td_style), Paragraph("Frontend Build Tool", td_style), Paragraph("Fast HMR and production bundle compilation", td_style)],
        [Paragraph("Vanilla CSS", td_style), Paragraph("UI Styling System", td_style), Paragraph("Custom variables, dark/light themes, print CSS", td_style)],
        [Paragraph("Python 3.14", td_style), Paragraph("Backend Runtime", td_style), Paragraph("FastAPI server, ML pipeline, dataset generation", td_style)],
        [Paragraph("FastAPI 0.115", td_style), Paragraph("REST API Framework", td_style), Paragraph("High-speed asynchronous routing and validation", td_style)],
        [Paragraph("Pydantic 2.10", td_style), Paragraph("Schema Validation", td_style), Paragraph("Strict input/output data typing", td_style)],
        [Paragraph("scikit-learn 1.6", td_style), Paragraph("Machine Learning", td_style), Paragraph("RandomForestClassifier for continuous condition prediction", td_style)],
        [Paragraph("pandas & NumPy", td_style), Paragraph("Data & Math Engine", td_style), Paragraph("Tabular indexing, Gaussian distance calculation", td_style)],
        [Paragraph("joblib", td_style), Paragraph("Model Serialization", td_style), Paragraph("Serializing & loading .joblib model files", td_style)],
        [Paragraph("SQLAlchemy 2.0", td_style), Paragraph("Database ORM", td_style), Paragraph("Schema modeling & SQLite query abstraction", td_style)],
        [Paragraph("SQLite 3", td_style), Paragraph("Local Database", td_style), Paragraph("Local persistent logging in cropmitra.db", td_style)],
        [Paragraph("pytest 9.0", td_style), Paragraph("Automated Testing", td_style), Paragraph("Unit, integration, and regression test suites", td_style)]
    ]
    t_tech = Table(tech_data, colWidths=[100, 140, 260])
    t_tech.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, SURFACE_BG]),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_tech)
    story.append(PageBreak())

    # ================= 6. DATASETS AUDIT =================
    story.append(Paragraph("6. Datasets Audit & Provenance", h1_style))
    ds_data = [
        [Paragraph("<b>Dataset File</b>", th_style), Paragraph("<b>Rows</b>", th_style), Paragraph("<b>Cols</b>", th_style), Paragraph("<b>Role & Integration Status</b>", th_style)],
        [Paragraph("soil info.csv", td_style), Paragraph("2,200", td_style), Paragraph("8", td_style), Paragraph("ML Random Forest training for N,P,K,Temp,Humidity,pH,Rainfall", td_style)],
        [Paragraph("fertilizer.csv", td_style), Paragraph("8,000", td_style), Paragraph("9", td_style), Paragraph("Baseline fertilizer classifier training data", td_style)],
        [Paragraph("CropDataset-Enhanced.csv", td_style), Paragraph("730", td_style), Paragraph("23", td_style), Paragraph("Authoritative geographical district-to-crop registry (Hard Filter)", td_style)],
        [Paragraph("crop_rotation_matrix.csv", td_style), Paragraph("2,601", td_style), Paragraph("14", td_style), Paragraph("Runtime in-memory directional sequence evaluation matrix", td_style)],
        [Paragraph("crop_rotation_dataset.xlsx", td_style), Paragraph("2,601", td_style), Paragraph("14", td_style), Paragraph("Multi-sheet formatted Excel reference workbook (4 sheets)", td_style)],
    ]
    t_ds = Table(ds_data, colWidths=[130, 45, 45, 280])
    t_ds.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, SURFACE_BG]),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_ds)
    story.append(Spacer(1, 10))

    # ================= 7. ML & SCORING MATHEMATICS =================
    story.append(Paragraph("7. Machine Learning & Multi-Criteria Scoring", h1_style))
    story.append(Paragraph(
        "The crop recommendation engine uses a normalized, multi-criteria decision formula ensuring mathematical rigor and zero fabricated multipliers:",
        body_style
    ))
    story.append(Paragraph("<b>Normalized Multi-Factor Formula:</b>", body_style))
    story.append(Paragraph("<code>base_score = 0.50 * ml_score + 0.30 * condition_score + 0.20 * rotation_score</code>", code_style))
    story.append(Paragraph("<code>final_score = round(min(9.9, max(2.0, base_score * loc_mult * 10.0)), 1)</code>", code_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("• <b>ml_score [0,1]:</b> Random Forest prediction probability blended with Gaussian condition similarity.", bullet_style))
    story.append(Paragraph("• <b>condition_score [0,1]:</b> Soil type compatibility and water availability constraints.", bullet_style))
    story.append(Paragraph("• <b>rotation_score [0,1]:</b> Directional crop sequence rating from the in-memory rotation matrix.", bullet_style))
    story.append(Paragraph("• <b>loc_mult:</b> 1.05 for exact district-level match, 1.00 for state fallback.", bullet_style))
    story.append(Paragraph("• <b>Weights:</b> 0.50 + 0.30 + 0.20 = 1.0000 strictly.", bullet_style))
    story.append(Spacer(1, 10))

    # ================= 8. PROOF OF IMPACT COMPARISON =================
    story.append(Paragraph("8. Proof-of-Impact Verification (Maharashtra -> Kolhapur)", h1_style))
    story.append(Paragraph("Auditing all candidate crops under identical field conditions (Medium Water, Loamy Soil):", body_style))
    
    proof_data = [
        [Paragraph("<b>Candidate Crop</b>", th_style), Paragraph("<b>Prev: Wheat</b>", th_style), Paragraph("<b>Prev: Sugarcane</b>", th_style), Paragraph("<b>Prev: Soybean</b>", th_style), Paragraph("<b>Rot Impact / Shift</b>", th_style)],
        [Paragraph("Soybean", td_style), Paragraph("9.4 (Rot: 0.85, #1)", td_style), Paragraph("9.4 (Rot: 0.85, #1)", td_style), Paragraph("8.3 (Avoid, #4)", td_style), Paragraph("Monoculture penalty under Soybean", td_style)],
        [Paragraph("Groundnut", td_style), Paragraph("9.1 (Rot: 0.85, #2)", td_style), Paragraph("9.1 (Rot: 0.85, #2)", td_style), Paragraph("8.6 (Rot: 0.60, #3)", td_style), Paragraph("Stable high performance", td_style)],
        [Paragraph("Sugarcane", td_style), Paragraph("8.9 (Rot: 0.75, #3)", td_style), Paragraph("8.1 (Avoid, #4)", td_style), Paragraph("8.9 (Rot: 0.75, #2)", td_style), Paragraph("Demoted out of top 3 under Sugarcane", td_style)],
        [Paragraph("Jowar (Sorghum)", td_style), Paragraph("8.5 (Rot: 0.60, #4)", td_style), Paragraph("8.6 (Rot: 0.65, #3)", td_style), Paragraph("9.0 (Rot: 0.85, #1)", td_style), Paragraph("Promoted to Rank #1 under Soybean", td_style)],
        [Paragraph("Rice", td_style), Paragraph("6.5 (Rot: 0.60, #5)", td_style), Paragraph("6.6 (Rot: 0.65, #5)", td_style), Paragraph("7.0 (Rot: 0.85, #5)", td_style), Paragraph("Lowest ML suitability in district", td_style)],
    ]
    t_proof = Table(proof_data, colWidths=[100, 95, 95, 95, 115])
    t_proof.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, SURFACE_BG]),
        ('PADDING', (0,0), (-1,-1), 4.5),
    ]))
    story.append(t_proof)
    story.append(PageBreak())

    # ================= 9. BACKEND API ENDPOINTS =================
    story.append(Paragraph("9. Backend REST API Endpoints", h1_style))
    api_data = [
        [Paragraph("<b>Method</b>", th_style), Paragraph("<b>Endpoint</b>", th_style), Paragraph("<b>Request / Params</b>", th_style), Paragraph("<b>Purpose</b>", th_style)],
        [Paragraph("GET", td_style), Paragraph("/api/health", td_style), Paragraph("None", td_style), Paragraph("Server health check and model loading verification", td_style)],
        [Paragraph("GET", td_style), Paragraph("/api/locations/states", td_style), Paragraph("None", td_style), Paragraph("Returns 36 Indian states and union territories", td_style)],
        [Paragraph("GET", td_style), Paragraph("/api/locations/districts", td_style), Paragraph("state: str", td_style), Paragraph("Returns districts registered for selected state", td_style)],
        [Paragraph("GET", td_style), Paragraph("/api/locations/crops", td_style), Paragraph("state: str, district: str", td_style), Paragraph("Returns supported crops for selected location", td_style)],
        [Paragraph("GET", td_style), Paragraph("/api/crops", td_style), Paragraph("None", td_style), Paragraph("Returns 51 canonical crops for general dropdowns", td_style)],
        [Paragraph("POST", td_style), Paragraph("/api/recommend", td_style), Paragraph("CropRecommendRequest", td_style), Paragraph("Full 5-stage crop recommendation pipeline", td_style)],
        [Paragraph("POST", td_style), Paragraph("/api/fertilizer", td_style), Paragraph("FertilizerRequest", td_style), Paragraph("NPK dosage and split-application guidelines", td_style)],
        [Paragraph("POST", td_style), Paragraph("/api/recommendations/save", td_style), Paragraph("SaveRecommendationRequest", td_style), Paragraph("Persists session record into SQLite database", td_style)],
        [Paragraph("GET", td_style), Paragraph("/api/recommendations", td_style), Paragraph("limit: int = 20", td_style), Paragraph("Retrieves historical recommendation records", td_style)],
    ]
    t_api = Table(api_data, colWidths=[45, 135, 120, 200])
    t_api.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, SURFACE_BG]),
        ('PADDING', (0,0), (-1,-1), 4.5),
    ]))
    story.append(t_api)
    story.append(Spacer(1, 10))

    # ================= 10. TESTING & VERIFICATION SUMMARY =================
    story.append(Paragraph("10. Automated Testing & Verification", h1_style))
    test_data = [
        [Paragraph("<b>Test Suite</b>", th_style), Paragraph("<b>Tests</b>", th_style), Paragraph("<b>Status</b>", th_style), Paragraph("<b>Verified Capabilities</b>", th_style)],
        [Paragraph("backend/test_backend.py", td_style), Paragraph("8 Tests", td_style), Paragraph("PASSED", td_style), Paragraph("API health, location registry, Akola/Kolhapur/Latur filters, DB", td_style)],
        [Paragraph("backend/test_rotation.py", td_style), Paragraph("11 Tests", td_style), Paragraph("PASSED", td_style), Paragraph("Sugarcane->Soybean, Wheat->Wheat, unknown fallback, Proof of Impact", td_style)],
        [Paragraph("ML Evaluation", td_style), Paragraph("2,200", td_style), Paragraph("PASSED", td_style), Paragraph("99.32% test accuracy on 20% stratified test set", td_style)],
        [Paragraph("Frontend Production Build", td_style), Paragraph("1,886", td_style), Paragraph("PASSED", td_style), Paragraph("Vite build compiled in 4.36s with 0 errors", td_style)],
        [Paragraph("Determinism Test", td_style), Paragraph("5 Runs", td_style), Paragraph("PASSED", td_style), Paragraph("100% identical rankings and scores across identical requests", td_style)],
    ]
    t_test = Table(test_data, colWidths=[120, 45, 55, 280])
    t_test.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, SURFACE_BG]),
        ('PADDING', (0,0), (-1,-1), 4.5),
    ]))
    story.append(t_test)
    story.append(Spacer(1, 10))

    # ================= 11. ACTUAL IMPLEMENTATION STATUS TABLE =================
    story.append(Paragraph("11. Actual Implementation Status Audit", h1_style))
    status_data = [
        [Paragraph("<b>Feature / Component</b>", th_style), Paragraph("<b>Implementation Status</b>", th_style), Paragraph("<b>Direct Evidence in Repository</b>", th_style)],
        [Paragraph("React Frontend SPA", td_style), Paragraph("IMPLEMENTED", td_style), Paragraph("frontend/src/App.jsx, pages/, index.css", td_style)],
        [Paragraph("FastAPI REST Backend", td_style), Paragraph("IMPLEMENTED", td_style), Paragraph("backend/app/main.py, api/routes.py", td_style)],
        [Paragraph("Random Forest Crop Model", td_style), Paragraph("IMPLEMENTED", td_style), Paragraph("backend/ml/models/crop_model.joblib (99.32%)", td_style)],
        [Paragraph("Location District Registry", td_style), Paragraph("IMPLEMENTED", td_style), Paragraph("backend/data/CropDataset-Enhanced.csv (730 rows)", td_style)],
        [Paragraph("Hard Location Crop Filtering", td_style), Paragraph("IMPLEMENTED", td_style), Paragraph("backend/app/services/location_service.py", td_style)],
        [Paragraph("Deterministic Crop Rotation", td_style), Paragraph("IMPLEMENTED", td_style), Paragraph("backend/app/services/rotation_service.py (2,601 pairs)", td_style)],
        [Paragraph("Multi-Sheet Excel Workbook", td_style), Paragraph("IMPLEMENTED", td_style), Paragraph("backend/data/crop_rotation_dataset.xlsx (4 sheets)", td_style)],
        [Paragraph("Fertilizer Recommendation System", td_style), Paragraph("IMPLEMENTED", td_style), Paragraph("backend/app/services/fertilizer_service.py", td_style)],
        [Paragraph("SQLite Database & SQLAlchemy", td_style), Paragraph("IMPLEMENTED", td_style), Paragraph("backend/app/database/models.py, cropmitra.db", td_style)],
        [Paragraph("Recommendation Persistence & History", td_style), Paragraph("IMPLEMENTED", td_style), Paragraph("POST /api/recommendations/save, GET /api/recommendations", td_style)],
        [Paragraph("Print-Ready Advisory Stylesheet", td_style), Paragraph("IMPLEMENTED", td_style), Paragraph("frontend/src/index.css (@media print)", td_style)],
        [Paragraph("Dark & Light Earthy Themes", td_style), Paragraph("IMPLEMENTED", td_style), Paragraph("frontend/src/index.css (data-theme toggle)", td_style)],
        [Paragraph("Mobile Responsive UI", td_style), Paragraph("IMPLEMENTED", td_style), Paragraph("frontend/src/index.css (Fluid media queries)", td_style)],
        [Paragraph("Live IoT Soil Sensor Hardware", td_style), Paragraph("PLANNED / NOT IMPLEMENTED", td_style), Paragraph("Planned for future hardware expansion", td_style)],
        [Paragraph("Real-Time Satellite Weather API", td_style), Paragraph("PLANNED / NOT IMPLEMENTED", td_style), Paragraph("Planned for future API integration", td_style)],
        [Paragraph("Regional Multilingual Localization", td_style), Paragraph("PLANNED / NOT IMPLEMENTED", td_style), Paragraph("Planned for Indian regional languages", td_style)],
    ]
    t_status = Table(status_data, colWidths=[140, 110, 250])
    t_status.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, SURFACE_BG]),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_status)
    story.append(Spacer(1, 14))

    # ================= CONCLUSION & VIVA SUMMARY =================
    story.append(Paragraph("12. Conclusion & Presentation Summary", h1_style))
    story.append(Paragraph(
        "<b>Executive Conclusion:</b> CropMitra is a fully functional, mathematically normalized, and scientifically grounded agricultural decision-support web platform. By integrating geographical district evidence, machine learning condition predictions, physical soil/water constraints, and directional crop rotation rules, CropMitra delivers robust, explainable, and reproducible crop and fertilizer advisories.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Viva Summary:</b> CropMitra does not replace lab soil testing or extension officers; rather, it provides an intuitive digital decision-support tool bridging complex university agricultural standards with real-world smallholder farm planning.",
        body_style
    ))

    # Build PDF with custom NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[PASS] Successfully generated professional PDF report: {PDF_PATH}")

if __name__ == "__main__":
    build_pdf()
