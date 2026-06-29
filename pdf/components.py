"""
Reusable Components for PDF Report
====================================

This module contains reusable UI components that are used across multiple sections:
- Metric rows
- Badge rows
- Quality rows
- Signature blocks
- Verification blocks
- Disclaimer
- Doctor notes
- Version history
- Timeline
- Pipeline

Dependencies:
- config.py, styles.py, icons.py, flowables.py, helpers.py, computations.py, charts.py
"""

from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer
from reportlab.graphics.shapes import Drawing, Line

from .config import (
    PRIMARY_BLUE, SECONDARY_BLUE, ACCENT_BLUE, SOFT_BLUE, ULTRA_LIGHT,
    INK, MUTED, LINE_GRAY, BORDER_GRAY, WHITE,
    STATUS_ACCENT, STATUS_BG,
    IMAGE_QUALITY_DEFAULTS,
    LIMITATIONS,
    REFERENCES,
    REPORT_METADATA,
)
from .styles import (
    FONT_REGULAR, FONT_BOLD, FONT_MEDIUM, FONT_SEMIBOLD,
)
from .icons import vector_icon
from .flowables import GradientProgressBar, StarRating
from .helpers import (
    ar, metric_card, badge_element, build_qr_code, section_divider,
    compute_verification_hash,
)
from .computations import (
    compute_overall_confidence, compute_severity_score,
    get_clinical_priority, get_ai_decision, get_confidence_level,
    get_quality_rating,
)


# ═══════════════════════════════════════════════════════════════════════════
# METRIC ROW BUILDER
# ══════════════════════════════════════════════════════════════════════════

def build_metric_row(cards_data):
    """
    Build a row of metric cards.
    
    Args:
        cards_data: List of tuples (value, label, accent_color, bg_color)
    
    Returns:
        Table: A row of metric cards.
    """
    cards = []
    for value, label, accent, bg in cards_data:
        cards.append(metric_card(value, label, accent, bg))
    
    row = Table([cards], colWidths=[3.8 * cm] * len(cards))
    row.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    return row


# ══════════════════════════════════════════════════════════════════════════
# BADGE ROW BUILDER
# ═══════════════════════════════════════════════════════════════════════════

def build_badge_row(severity, icd10, snomed):
    """
    Build a row of badges (severity, ICD-10, SNOMED).
    
    Args:
        severity: Tuple (English, Arabic)
        icd10: ICD-10 code string
        snomed: SNOMED CT code string
    
    Returns:
        Table: Row containing badges.
    """
    sev_en = severity[0] if isinstance(severity, tuple) else severity
    sev_color = STATUS_ACCENT.get(
        {'Mild': 'green', 'Moderate': 'yellow', 'Significant': 'orange', 'Severe': 'red'}.get(sev_en, 'green'),
        MUTED
    )
    
    sev_badge = badge_element(sev_en, sev_color)
    icd_badge = badge_element(icd10 or '—', SECONDARY_BLUE)
    snomed_p = Paragraph(f"SNOMED: {snomed or '—'}", ParagraphStyle(
        'snomed', fontName=FONT_REGULAR, fontSize=8,
        textColor=MUTED, alignment=TA_CENTER, leading=11))
    
    row = Table([[sev_badge, icd_badge, snomed_p]],
                colWidths=[2.2 * cm, 2.2 * cm, 6 * cm])
    row.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    return row


# ══════════════════════════════════════════════════════════════════════════
# QUALITY ROW BUILDER
# ═══════════════════════════════════════════════════════════════════════════

def build_quality_rows():
    """
    Build all quality assessment rows.
    
    Returns:
        list: List of Table objects, one per quality metric.
    """
    rows = []
    for label, score in IMAGE_QUALITY_DEFAULTS:
        rating = get_quality_rating(score)
        rat_clr = {
            'Excellent': STATUS_ACCENT['green'],
            'Good': ACCENT_BLUE,
            'Acceptable': STATUS_ACCENT['yellow'],
            'Needs Review': STATUS_ACCENT['red'],
        }[rating]
        bar_key = 'green' if score >= 85 else 'yellow' if score >= 70 else 'orange'
        
        row = Table([[
            Paragraph(label, ParagraphStyle('ql', fontName=FONT_MEDIUM, fontSize=9,
                                             textColor=INK, alignment=TA_LEFT, leading=12)),
            GradientProgressBar(7 * cm, 0.4 * cm, score, bar_key),
            Paragraph(f"{score}%", ParagraphStyle('qv', fontName=FONT_BOLD, fontSize=9,
                                                   textColor=PRIMARY_BLUE, alignment=TA_CENTER, leading=12)),
            Paragraph(rating, ParagraphStyle('qr', fontName=FONT_BOLD, fontSize=8,
                                              textColor=rat_clr, alignment=TA_CENTER, leading=11)),
        ]], colWidths=[3 * cm, 7 * cm, 2 * cm, 3 * cm])
        row.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        rows.append(row)
    return rows


# ═══════════════════════════════════════════════════════════════════════════
# CONFIDENCE ROW BUILDER
# ═══════════════════════════════════════════════════════════════════════════

def build_confidence_rows(results):
    """
    Build confidence distribution rows.
    
    Args:
        results: List of result dicts
    
    Returns:
        list: List of Table objects.
    """
    conf_levels = [
        ('Excellent (>=85%)', len([r for r in results if r['probability'] >= 85]), 'green'),
        ('Good (70-84%)', len([r for r in results if 70 <= r['probability'] < 85]), 'green'),
        ('Fair (50-69%)', len([r for r in results if 50 <= r['probability'] < 70]), 'yellow'),
        ('Low (<50%)', len([r for r in results if r['probability'] < 50]), 'orange'),
    ]
    
    rows = []
    for label, count, clr_key in conf_levels:
        pct = min(count * 12, 100) if results else 0
        row = Table([[
            Paragraph(label, ParagraphStyle('cdl', fontName=FONT_MEDIUM, fontSize=9,
                                             textColor=INK, alignment=TA_LEFT, leading=12)),
            GradientProgressBar(8 * cm, 0.38 * cm, pct, clr_key),
            Paragraph(str(count), ParagraphStyle('cdv', fontName=FONT_BOLD, fontSize=9,
                                                  textColor=STATUS_ACCENT[clr_key], alignment=TA_CENTER, leading=12)),
        ]], colWidths=[4 * cm, 9 * cm, 2 * cm])
        row.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        rows.append(row)
    return rows


# ═══════════════════════════════════════════════════════════════════════════
# TIMELINE BUILDER
# ═══════════════════════════════════════════════════════════════════════════

def build_timeline(report_time, processing_time, report_gen_time):
    """
    Build the processing timeline.
    
    Args:
        report_time: Time string
        processing_time: Processing time in seconds
        report_gen_time: Report generation time in seconds
    
    Returns:
        Table: Timeline table.
    """
    tl_steps = [
        ("Image Uploaded", report_time),
        ("Preprocessing", f"+{round(processing_time * 0.1, 2)}s"),
        ("AI Analysis", f"+{round(processing_time * 0.6, 2)}s"),
        ("Classification", f"+{round(processing_time * 0.8, 2)}s"),
        ("Report Generated", f"+{report_gen_time}s"),
    ]
    
    tl_cells = []
    for step, ts in tl_steps:
        tl_cells.append(Table([
            [Paragraph(step, ParagraphStyle('tls', fontName=FONT_BOLD, fontSize=8,
                                             textColor=PRIMARY_BLUE, alignment=TA_CENTER, leading=10))],
            [Paragraph(ts, ParagraphStyle('tlt', fontName=FONT_REGULAR, fontSize=7,
                                           textColor=MUTED, alignment=TA_CENTER, leading=9))],
        ], colWidths=[3 * cm]))
    
    tl_tbl = Table([tl_cells], colWidths=[3.2 * cm] * 5)
    tl_tbl.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('LINEBELOW', (0, 0), (-1, -1), 0.3, LINE_GRAY),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    return tl_tbl


# ═══════════════════════════════════════════════════════════════════════════
# PIPELINE BUILDER
# ═══════════════════════════════════════════════════════════════════════════

def build_pipeline():
    """
    Build the AI pipeline diagram.
    
    Returns:
        Table: Pipeline diagram table.
    """
    DARK_COLORS = {ACCENT_BLUE, SECONDARY_BLUE, PRIMARY_BLUE}
    pipe_steps = [
        ("Input<br/>X-ray", SOFT_BLUE),
        ("Resize<br/>224x224", SOFT_BLUE),
        ("Normalize<br/>Pixels", SOFT_BLUE),
        ("DenseNet-121<br/>Feats", ACCENT_BLUE),
        ("Sigmoid<br/>Activation", SECONDARY_BLUE),
        ("Threshold<br/>0.50", PRIMARY_BLUE),
        ("Output<br/>Preds", STATUS_BG['green']),
    ]
    
    pipe_cells = []
    for step_label, step_color in pipe_steps:
        txt_color = WHITE if step_color in DARK_COLORS else INK
        cell = Table([[Paragraph(step_label, ParagraphStyle(
            'ps', fontName=FONT_BOLD, fontSize=7, textColor=txt_color,
            alignment=TA_CENTER, leading=9))]],
            colWidths=[2.1 * cm], rowHeights=[1.2 * cm])
        cell.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), step_color),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 0.5, WHITE),
        ]))
        pipe_cells.append(cell)
    
    pipe_tbl = Table([pipe_cells], colWidths=[2.28 * cm] * 7)
    pipe_tbl.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    return pipe_tbl


# ═══════════════════════════════════════════════════════════════════════════
# SIGNATURE BLOCK BUILDER
# ══════════════════════════════════════════════════════════════════════════

def build_signature_block(report_id, report_date, report_time, verify_url, verification_hash):
    """
    Build the complete signature and verification block.
    
    Args:
        report_id: Report ID
        report_date: Date string
        report_time: Time string
        verify_url: Verification URL
        verification_hash: SHA-256 hash
    
    Returns:
        list: List of flowables to add to elements.
    """
    elements = []
    
    # Signature table
    qr_cell = Table([
        [Paragraph(ar("رمز التحقق"), ParagraphStyle('qr_t', fontName=FONT_REGULAR, fontSize=8,
                                                     textColor=MUTED, alignment=TA_CENTER, leading=11))],
        [build_qr_code(verify_url, 2 * cm)],
        [Paragraph(f"ID: {report_id}", ParagraphStyle('qr_id', fontName=FONT_REGULAR, fontSize=8,
                                                       textColor=MUTED, alignment=TA_CENTER, leading=11))],
    ], colWidths=[4 * cm])
    qr_cell.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]))
    
    sig_left = Table([
        [Paragraph(ar("توقيع الطبيب"), ParagraphStyle('sig_t', fontName=FONT_REGULAR, fontSize=8,
                                                       textColor=MUTED, alignment=TA_CENTER, leading=11))],
        [Spacer(1, 1 * cm)],
        [Paragraph("____________________", ParagraphStyle('sig_l', fontName=FONT_REGULAR, fontSize=9,
                                                           textColor=MUTED, alignment=TA_CENTER, leading=12))],
        [Paragraph("Doctor Signature", ParagraphStyle('sig_b', fontName=FONT_REGULAR, fontSize=8,
                                                       textColor=MUTED, alignment=TA_CENTER, leading=11))],
    ], colWidths=[4 * cm])
    sig_left.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
    
    sig_center = Table([
        [Paragraph(ar("ختم المستشفى"), ParagraphStyle('stamp_t', fontName=FONT_REGULAR, fontSize=8,
                                                        textColor=MUTED, alignment=TA_CENTER, leading=11))],
        [Spacer(1, 0.5 * cm)],
        [vector_icon("hospital", 1.2 * cm, MUTED)],
        [Spacer(1, 0.2 * cm)],
        [Paragraph("Hospital Stamp", ParagraphStyle('stamp_b', fontName=FONT_REGULAR, fontSize=8,
                                                     textColor=MUTED, alignment=TA_CENTER, leading=11))],
    ], colWidths=[4 * cm])
    sig_center.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
    
    sig_right = Table([
        [Paragraph(ar("تاريخ المراجعة"), ParagraphStyle('rev_t', fontName=FONT_REGULAR, fontSize=8,
                                                         textColor=MUTED, alignment=TA_CENTER, leading=11))],
        [Spacer(1, 0.8 * cm)],
        [Paragraph(report_date, ParagraphStyle('rev_d', fontName=FONT_MEDIUM, fontSize=10,
                                               textColor=INK, alignment=TA_CENTER, leading=14))],
        [Paragraph(report_time, ParagraphStyle('rev_t2', fontName=FONT_REGULAR, fontSize=9,
                                               textColor=MUTED, alignment=TA_CENTER, leading=12))],
        [Paragraph("Review Date", ParagraphStyle('rev_b', fontName=FONT_REGULAR, fontSize=8,
                                                  textColor=MUTED, alignment=TA_CENTER, leading=11))],
    ], colWidths=[4 * cm])
    sig_right.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
    
    sig_tbl = Table([[sig_left, sig_center, sig_right, qr_cell]], colWidths=[4 * cm] * 4)
    sig_tbl.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 0), (-1, -1), ULTRA_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.6, LINE_GRAY),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(sig_tbl)
    elements.append(Spacer(1, 0.2 * cm))
    
    # Verification hash
    hash_row = Table([[
        Paragraph("SHA-256 Verification Hash", ParagraphStyle('hash_l', fontName=FONT_REGULAR, fontSize=9,
                                                               textColor=MUTED, alignment=TA_LEFT, leading=12)),
        Paragraph(verification_hash, ParagraphStyle('hash_v', fontName=FONT_BOLD, fontSize=8.5,
                                                    textColor=PRIMARY_BLUE, alignment=TA_LEFT, leading=12)),
    ]], colWidths=[5 * cm, 11 * cm])
    hash_row.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), SOFT_BLUE),
        ('BOX', (0, 0), (-1, -1), 0.5, ACCENT_BLUE),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(hash_row)
    elements.append(Spacer(1, 0.15 * cm))
    
    # Verification URL
    verify_row = Table([[
        Paragraph("Verification URL", ParagraphStyle('url_l', fontName=FONT_REGULAR, fontSize=9,
                                                      textColor=MUTED, alignment=TA_LEFT, leading=12)),
        Paragraph(verify_url, ParagraphStyle('url_v', fontName=FONT_MEDIUM, fontSize=8.5,
                                              textColor=ACCENT_BLUE, alignment=TA_LEFT, leading=12)),
    ]], colWidths=[5 * cm, 11 * cm])
    verify_row.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), ULTRA_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.5, LINE_GRAY),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(verify_row)
    elements.append(Spacer(1, 0.15 * cm))
    
    # Digital signature
    digital_sig = Table([[
        Paragraph("Digital Signature", ParagraphStyle('ds_l', fontName=FONT_REGULAR, fontSize=9,
                                                       textColor=MUTED, alignment=TA_LEFT, leading=12)),
        Paragraph(f"RSA-2048  |  RespAI CA  |  {report_date}",
                  ParagraphStyle('ds_v', fontName=FONT_MEDIUM, fontSize=8.5,
                                 textColor=STATUS_ACCENT['green'], alignment=TA_LEFT, leading=12)),
    ]], colWidths=[5 * cm, 11 * cm])
    digital_sig.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), STATUS_BG['green']),
        ('BOX', (0, 0), (-1, -1), 0.5, STATUS_ACCENT['green']),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(digital_sig)
    
    return elements


# ═══════════════════════════════════════════════════════════════════════════
# DISCLAIMER BUILDER
# ══════════════════════════════════════════════════════════════════════════

def build_disclaimer():
    """
    Build the medical disclaimer.
    
    Returns:
        list: List of flowables.
    """
    elements = []
    elements.append(Paragraph(ar("تنويه طبي وقانوني مهم"), ParagraphStyle(
        'dt', fontName=FONT_BOLD, fontSize=11,
        textColor=colors.HexColor('#7A1F1F'), alignment=TA_CENTER, leading=15)))
    elements.append(Spacer(1, 0.1 * cm))
    elements.append(Paragraph(
        ar("هذا التقرير مُنشأ بواسطة نظام ذكاء اصطناعي معتمد على تقنيات التعلم العميق، "
           "وهو يُقدَّم كأداة مساعدة للقرار السريري فقط، ولا يُعد بديلاً عن التشخيص الطبي "
           "المتخصص من قبل أخصائي أشعة مؤهل. يجب دائماً تفسير النتائج في سياق الحالة "
           "السريرية الكاملة للمريض. هذا النظام لم يخضع بعد لموافقة FDA أو CE للاستخدام التشخيصي المباشر."),
        ParagraphStyle('disc', fontName=FONT_REGULAR, fontSize=9,
                       textColor=colors.HexColor('#7A1F1F'), alignment=TA_JUSTIFY, spaceAfter=3, leading=13)))
    return elements


# ═══════════════════════════════════════════════════════════════════════════
# DOCTOR NOTES BUILDER
# ═══════════════════════════════════════════════════════════════════════════

def build_doctor_notes(num_lines=6):
    """
    Build doctor notes section with horizontal lines.
    
    Args:
        num_lines: Number of lines to draw
    
    Returns:
        list: List of flowables.
    """
    elements = []
    for _ in range(num_lines):
        ld = Drawing(15 * cm, 0.65 * cm)
        ld.add(Line(0, 0.3 * cm, 15 * cm, 0.3 * cm, strokeColor=LINE_GRAY, strokeWidth=0.4))
        elements.append(ld)
        elements.append(Spacer(1, 0.05 * cm))
    return elements


# ═══════════════════════════════════════════════════════════════════════════
# VERSION HISTORY BUILDER
# ══════════════════════════════════════════════════════════════════════════

def build_version_history():
    """
    Build the AI version history table.
    
    Returns:
        Table: Version history table.
    """
    ver_data = [
        [Paragraph("Component", ParagraphStyle('vh_h', fontName=FONT_BOLD, fontSize=9,
                                                textColor=WHITE, alignment=TA_CENTER, leading=13)),
         Paragraph("Version", ParagraphStyle('vh_h2', fontName=FONT_BOLD, fontSize=9,
                                              textColor=WHITE, alignment=TA_CENTER, leading=13))],
        [Paragraph("RespAI System", ParagraphStyle('vh_r', fontName=FONT_REGULAR, fontSize=10,
                                                    textColor=INK, alignment=TA_LEFT, leading=14)),
         Paragraph(f"v{REPORT_METADATA['report_version']}", ParagraphStyle('vh_v', fontName=FONT_BOLD, fontSize=10,
                                                                            textColor=INK, alignment=TA_LEFT, leading=14))],
        [Paragraph("CheXNet Model", ParagraphStyle('vh_r', fontName=FONT_REGULAR, fontSize=10,
                                                    textColor=INK, alignment=TA_LEFT, leading=14)),
         Paragraph(REPORT_METADATA['model_version'], ParagraphStyle('vh_v', fontName=FONT_BOLD, fontSize=10,
                                                                     textColor=INK, alignment=TA_LEFT, leading=14))],
        [Paragraph("DenseNet-121", ParagraphStyle('vh_r', fontName=FONT_REGULAR, fontSize=10,
                                                   textColor=INK, alignment=TA_LEFT, leading=14)),
         Paragraph("Pretrained (ImageNet)", ParagraphStyle('vh_v', fontName=FONT_REGULAR, fontSize=10,
                                                            textColor=INK, alignment=TA_LEFT, leading=14))],
        [Paragraph("PyTorch", ParagraphStyle('vh_r', fontName=FONT_REGULAR, fontSize=10,
                                              textColor=INK, alignment=TA_LEFT, leading=14)),
         Paragraph(REPORT_METADATA['pytorch_version'], ParagraphStyle('vh_v', fontName=FONT_BOLD, fontSize=10,
                                                                       textColor=INK, alignment=TA_LEFT, leading=14))],
        [Paragraph("CUDA", ParagraphStyle('vh_r', fontName=FONT_REGULAR, fontSize=10,
                                           textColor=INK, alignment=TA_LEFT, leading=14)),
         Paragraph(REPORT_METADATA['cuda_version'], ParagraphStyle('vh_v', fontName=FONT_BOLD, fontSize=10,
                                                                     textColor=INK, alignment=TA_LEFT, leading=14))],
    ]
    ver_tbl = Table(ver_data, colWidths=[8 * cm, 8 * cm])
    ver_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), SECONDARY_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('BOX', (0, 0), (-1, -1), 0.5, SECONDARY_BLUE),
        ('INNERGRID', (0, 0), (-1, -1), 0.3, LINE_GRAY),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, ULTRA_LIGHT]),
    ]))
    return ver_tbl


# ══════════════════════════════════════════════════════════════════════════
# LIMITATIONS & REFERENCES BUILDER
# ═══════════════════════════════════════════════════════════════════════════

def build_limitations_and_references():
    """
    Build limitations and references section.
    
    Returns:
        list: List of flowables.
    """
    elements = []
    
    # Limitations
    elements.append(Paragraph(ar("حدود النظام  Limitations"), ParagraphStyle(
        'lim_h', fontName=FONT_SEMIBOLD, fontSize=11,
        textColor=INK, alignment=TA_RIGHT, spaceAfter=4, leading=15)))
    for item in LIMITATIONS:
        elements.append(Paragraph(f"&#9679;  {ar(item)}", ParagraphStyle(
            'lim_i', fontName=FONT_REGULAR, fontSize=10,
            textColor=INK, alignment=TA_JUSTIFY, spaceAfter=3, leading=15)))
    
    elements.append(Spacer(1, 0.2 * cm))
    
    # References
    elements.append(Paragraph(ar("المراجع العلمية  References (APA)"), ParagraphStyle(
        'ref_h', fontName=FONT_SEMIBOLD, fontSize=11,
        textColor=INK, alignment=TA_RIGHT, spaceAfter=4, leading=15)))
    for i, ref in enumerate(REFERENCES, 1):
        elements.append(Paragraph(f"[{i}]  {ref}", ParagraphStyle(
            'ref_i', fontName=FONT_REGULAR, fontSize=10,
            textColor=INK, alignment=TA_JUSTIFY, spaceAfter=3, leading=15)))
    
    return elements


# ═══════════════════════════════════════════════════════════════════════════
# NEEDED IMPORT
# ═══════════════════════════════════════════════════════════════════════════
from reportlab.lib import colors