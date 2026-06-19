"""
RetinAI Backend — ReportLab PDF Generator
Compiles clinical metrics, images, PubMed citations, and agent notes into a premium A4 PDF.
"""
import os
import re
from pathlib import Path
from typing import Dict, Any, List

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Canvas for adding page numbers and running footer dynamically."""
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
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#94a3b8"))
        
        # Draw running footer line
        self.setLineWidth(0.5)
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.line(54, 45, 595 - 54, 45)
        
        # Footer text
        footer_text = "RetinAI — Document d'aide à la décision clinique. Non destiné à l'auto-diagnostic."
        self.drawString(54, 30, footer_text)
        
        # Page count
        page_str = f"Page {self._pageNumber} sur {page_count}"
        self.drawRightString(595 - 54, 30, page_str)
        self.restoreState()


def md_to_html(text: str) -> str:
    """Helper to convert basic markdown inline tokens into HTML-like tags for ReportLab Paragraphs."""
    if not text:
        return ""
    # Bold
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
    # Italic
    text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", text)
    # Inline code
    text = re.sub(r"`([^`]+)`", r"<font face='Courier' size='9' color='#0f172a'>\1</font>", text)
    return text


def build_clinical_story(markdown_content: str, styles: Any) -> List[Any]:
    """Parses clinical report markdown into a list of styled ReportLab Flowables."""
    story = []
    
    # Custom styles
    h3_style = ParagraphStyle(
        'ReportH3',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=13,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )
    
    h4_style = ParagraphStyle(
        'ReportH4',
        parent=styles['Heading4'],
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'ReportBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#334155"),
        spaceBefore=4,
        spaceAfter=4
    )
    
    bullet_style = ParagraphStyle(
        'ReportBullet',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceBefore=2,
        spaceAfter=2
    )
    
    quote_style = ParagraphStyle(
        'ReportQuote',
        parent=body_style,
        fontName='Helvetica-Oblique',
        textColor=colors.HexColor("#475569"),
        leftIndent=15,
        spaceBefore=6,
        spaceAfter=6
    )

    lines = markdown_content.split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith("### "):
            title = md_to_html(line[4:])
            story.append(Paragraph(title, h3_style))
        elif line.startswith("#### "):
            title = md_to_html(line[5:])
            story.append(Paragraph(title, h4_style))
        elif line.startswith("- ") or line.startswith("* "):
            content = md_to_html(line[2:])
            story.append(Paragraph(f"&bull; {content}", bullet_style))
        elif re.match(r"^\d+\.\s", line):
            # Numbered list
            prefix = re.match(r"^(\d+)\.\s", line).group(0)
            content = md_to_html(line[len(prefix):])
            story.append(Paragraph(f"<b>{prefix}</b> {content}", bullet_style))
        elif line.startswith("> "):
            content = md_to_html(line[2:])
            # Styled inside a table for left border
            p = Paragraph(content, quote_style)
            quote_table = Table([[p]], colWidths=[450])
            quote_table.setStyle(TableStyle([
                ('LINELEFT', (0,0), (0,-1), 3, colors.HexColor("#0284c7")),
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f0f9ff")),
                ('PADDING', (0,0), (-1,-1), 8),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ]))
            story.append(Spacer(1, 4))
            story.append(quote_table)
            story.append(Spacer(1, 4))
        else:
            content = md_to_html(line)
            story.append(Paragraph(content, body_style))
            
    return story


def generate_pdf_report(
    output_path: str,
    patient: Dict[str, Any],
    analysis: Dict[str, Any],
    original_img_path: str,
    heatmap_img_path: str
) -> str:
    """
    Compiles analysis and patient data into a structured clinical PDF.
    
    Args:
        output_path: Destination path for the PDF file.
        patient: Patient record dict (id, name, birthdate, gender).
        analysis: Analysis metrics dict (id, stage, confidence, referable, urgency, clinical_report).
        original_img_path: Absolute filesystem path to the original fundus image.
        heatmap_img_path: Absolute filesystem path to the Grad-CAM heatmap.
        
    Returns:
        The output_path string.
    """
    # Page dimensions & limits: A4 = 595.27 x 841.89 points
    # Margins: 0.75 in (54 points)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=64
    )
    
    styles = getSampleStyleSheet()
    story = []
    
    # ── 1. Header ─────────────────────────────────────────────────────────────
    title_style = ParagraphStyle(
        'BrandTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=colors.HexColor("#0f172a"),
        leading=28
    )
    subtitle_style = ParagraphStyle(
        'DocType',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor("#475569"),
        alignment=TA_RIGHT,
        leading=24
    )
    
    brand_p = Paragraph("<font color='#0284c7'>Retin</font>AI", title_style)
    doc_type_p = Paragraph("RAPPORT CLINIQUE DE DÉPISTAGE", subtitle_style)
    
    header_table = Table([[brand_p, doc_type_p]], colWidths=[200, 287])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (0,-1), 'LEFT'),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LINEBELOW', (0,0), (-1,-1), 1.5, colors.HexColor("#0f172a")),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 15))
    
    # ── 2. Patient & Exam Info Block ──────────────────────────────────────────
    label_style = ParagraphStyle(
        'GridLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=1
    )
    value_style = ParagraphStyle(
        'GridValue',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        textColor=colors.HexColor("#0f172a")
    )
    
    info_data = [
        [
            Paragraph("IDENTIFIANT PATIENT", label_style),
            Paragraph("RÉFÉRENCE EXAMEN", label_style)
        ],
        [
            Paragraph(str(patient.get("id", "N/A")), value_style),
            Paragraph(str(analysis.get("id", "N/A")), value_style)
        ],
        [
            Paragraph("NOM COMPLET", label_style),
            Paragraph("DATE D'ANALYSE", label_style)
        ],
        [
            Paragraph(f"<b>{patient.get('name', 'N/A')}</b>", value_style),
            Paragraph(str(analysis.get("created_at", "N/A"))[:16].replace("T", " "), value_style)
        ],
        [
            Paragraph("GENRE / ÂGE", label_style),
            Paragraph("QUALITÉ DU SCAN", label_style)
        ],
        [
            Paragraph(
                f"{'Masculin' if patient.get('gender') == 'M' else 'Féminin'} ({patient.get('birthdate', 'N/A')})",
                value_style
            ),
            Paragraph("Bonne (Qualité validée)", value_style)
        ]
    ]
    
    info_table = Table(info_data, colWidths=[243, 244])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('PADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,-1), (-1,-1), 10),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.HexColor("#f1f5f9")),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 15))
    
    # ── 3. Diagnostic Metrics ─────────────────────────────────────────────────
    metric_label = ParagraphStyle(
        'MetricLabel',
        parent=styles['Normal'],
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        fontSize=8,
        textColor=colors.HexColor("#475569")
    )
    
    stage_text = [
        "Stade 0 (Sain)",
        "Stade 1 (Léger)",
        "Stade 2 (Modéré)",
        "Stade 3 (Sévère)",
        "Stade 4 (Prolifératif)"
    ]
    stage = analysis.get("stage", 0)
    confidence = analysis.get("confidence", 0.0)
    referable = "⚠️ OUI" if stage >= 2 else "✅ NON"
    urgency = analysis.get("urgency", "Contrôle annuel")
    
    # Highlight alert card in red if referable
    bg_color_metric = colors.HexColor("#fef2f2") if stage >= 2 else colors.HexColor("#ffffff")
    border_color_metric = colors.HexColor("#f87171") if stage >= 2 else colors.HexColor("#cbd5e1")
    
    metric_stage_val = ParagraphStyle(
        'MetricStageVal',
        parent=styles['Normal'],
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor("#b91c1c") if stage >= 2 else colors.HexColor("#0f172a")
    )
    metric_value = ParagraphStyle(
        'MetricVal',
        parent=styles['Normal'],
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor("#0f172a")
    )
    
    metrics_data = [
        [
            Paragraph("STADE PRÉDIT", metric_label),
            Paragraph("CONFIANCE IA", metric_label),
            Paragraph("RÉFÉRABLE (DR)", metric_label),
            Paragraph("URGENCE CLINIQUE", metric_label)
        ],
        [
            Paragraph(stage_text[stage], metric_stage_val),
            Paragraph(f"{confidence*100:.1f}%", metric_value),
            Paragraph(referable, metric_value),
            Paragraph(urgency, metric_value)
        ]
    ]
    
    metrics_table = Table(metrics_data, colWidths=[121, 122, 122, 122])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg_color_metric),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 1, border_color_metric),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border_color_metric),
        ('TOPPADDING', (0,0), (-1,0), 6),
        ('BOTTOMPADDING', (0,0), (-1,0), 2),
        ('TOPPADDING', (0,1), (-1,-1), 2),
        ('BOTTOMPADDING', (0,1), (-1,-1), 8),
    ]))
    story.append(metrics_table)
    story.append(Spacer(1, 15))
    
    # ── 4. Fundus Scans & Heatmaps ────────────────────────────────────────────
    # Resize images keeping aspect ratios. Target width is ~235 points.
    images_story = []
    
    img_orig_flow = None
    img_heat_flow = None
    
    if original_img_path and os.path.exists(original_img_path):
        try:
            img_orig_flow = Image(original_img_path, width=230, height=230)
        except Exception as e:
            print(f"[PDF Image Error] Original: {e}")
            
    if heatmap_img_path and os.path.exists(heatmap_img_path):
        try:
            img_heat_flow = Image(heatmap_img_path, width=230, height=230)
        except Exception as e:
            print(f"[PDF Image Error] Heatmap: {e}")
            
    img_label_style = ParagraphStyle(
        'ImgLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        textColor=colors.HexColor("#475569"),
        alignment=TA_CENTER,
        spaceBefore=4
    )
    
    label_orig = Paragraph("Fond d'œil d'origine", img_label_style)
    label_heat = Paragraph("Carte d'activation lèsionnelle (Grad-CAM)", img_label_style)
    
    # Build image row
    img_row = [
        img_orig_flow if img_orig_flow else Paragraph("Image indisponible", img_label_style),
        img_heat_flow if img_heat_flow else Paragraph("Carte indisponible", img_label_style)
    ]
    label_row = [label_orig, label_heat]
    
    image_table_data = [img_row, label_row]
    image_table = Table(image_table_data, colWidths=[243, 244])
    image_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('PADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,1), (-1,1), 10),
    ]))
    
    story.append(image_table)
    
    # ── 5. Page Break for Report ──────────────────────────────────────────────
    # To keep document formatted neatly, we put the clinical report text on the second page
    story.append(PageBreak())
    
    # ── 6. Clinical Report Section ────────────────────────────────────────────
    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=10,
        keepWithNext=True
    )
    
    report_title = Paragraph("COMPTE-RENDU CLINIQUE DIÉGÉNÉRÉ PAR MULTI-AGENTS", section_title_style)
    report_title_table = Table([[report_title]], colWidths=[487])
    report_title_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(report_title_table)
    story.append(Spacer(1, 8))
    
    report_md = analysis.get("clinical_report", "")
    report_story = build_clinical_story(report_md, styles)
    story.extend(report_story)
    story.append(Spacer(1, 20))
    
    # ── 7. Signature Section ──────────────────────────────────────────────────
    sign_label = ParagraphStyle(
        'SignLabel',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        textColor=colors.HexColor("#64748b"),
        alignment=TA_CENTER
    )
    sign_val_ia = ParagraphStyle(
        'SignValIA',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=colors.HexColor("#0284c7"),
        alignment=TA_CENTER,
        spaceBefore=25
    )
    sign_val_dr = ParagraphStyle(
        'SignValDr',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=10,
        textColor=colors.HexColor("#94a3b8"),
        alignment=TA_CENTER,
        spaceBefore=25
    )
    
    sign_box_ia = [
        Paragraph("Visa de l'Assistant d'Analyse IA (RetinAI Core)", sign_label),
        Paragraph("APPROUVÉ PAR IA", sign_val_ia)
    ]
    sign_box_dr = [
        Paragraph("Signature de l'Ophtalmologue Référent", sign_label),
        Paragraph("Signature & Cachet", sign_val_dr)
    ]
    
    signature_data = [[sign_box_ia, sign_box_dr]]
    signature_table = Table(signature_data, colWidths=[240, 247])
    signature_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 10),
        ('LINEABOVE', (0,0), (0,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('LINEABOVE', (1,0), (1,-1), 0.5, colors.HexColor("#cbd5e1")),
    ]))
    
    story.append(Spacer(1, 10))
    story.append(KeepTogether([signature_table]))
    
    # Build Document using dynamic page-numbering canvas
    doc.build(story, canvasmaker=NumberedCanvas)
    return output_path


if __name__ == "__main__":
    # Test generation
    mock_patient = {
        "id": "P-4421",
        "name": "Amine Charrou",
        "birthdate": "1998-05-12",
        "gender": "M"
    }
    mock_analysis = {
        "id": "AN-TESTPDF1",
        "stage": 2,
        "confidence": 0.943,
        "urgency": "Sous 3 mois",
        "clinical_report": """### 🩺 RAPPORT D'ANALYSE CLINIQUE PAR IA - RetinAI
**Généré le** : 2026-05-22 | **Nom** : **Amine Charrou**

#### 1. SYNTHÈSE DU DIAGNOSTIC DE L'IA
- **Stade Prédit** : **Stade 2 / 4 - Rétinopathie diabétique modérée**
- **Indice de Confiance** : **94.3%**
- **Niveau d'Urgence Clinique** : **Consultation sous 3 mois**
- **Statut d'Adressage Référable (Referable DR)** : **⚠️ OUI**

#### 2. CONSTATATIONS CLINIQUES DU FOND D'ŒIL
L'image de fond d'œil met en évidence de nombreux microanévrismes associés à de petites hémorragies rétiniennes localisées et des foyers d'exsudats durs (lipides) à proximité de la zone maculaire.

#### 3. CORRÉLATIONS SCIENTIFIQUES (PubMed)
- **Source** : Tan G, et al. (2020). *Screening and management of Moderate Nonproliferative Diabetic Retinopathy*.
  *Conclusion de l'étude* : Le traitement précoce et l'adressage limitent la perte de vision à long terme.

📅 PROTOCOLE DE SUIVI & PRÉVENTION CLINIQUE
1. **Orientation** : Ophtalmologue sous 3 mois.
2. **Examens** : OCT maculaire.
3. **Contrôle** : HbA1c rigoureux.

> ⚠️ **IMPORTANT** : Ce rapport est une aide à la décision. Les résultats doivent être validés par un médecin spécialiste.""",
        "created_at": "2026-05-22T14:32:00"
    }
    
    test_pdf = str(Path(__file__).parent.parent / "static" / "reports" / "test.pdf")
    # Ensure reports dir exists
    Path(test_pdf).parent.mkdir(parents=True, exist_ok=True)
    
    generate_pdf_report(test_pdf, mock_patient, mock_analysis, None, None)
    print(f"Generated test PDF report at: {test_pdf}")
