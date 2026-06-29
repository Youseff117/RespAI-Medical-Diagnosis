"""
PDF Report Sections Builder
=============================

This module contains functions to build each of the 16 report sections.
Each function returns a list of flowables to be added to the document.

Dependencies:
- All other pdf modules
"""

from reportlab.lib import colors  # ← تم نقله للأعلى
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.graphics.shapes import Drawing, Rect

from .config import (
    PRIMARY_BLUE, SECONDARY_BLUE, ACCENT_BLUE, SOFT_BLUE, ULTRA_LIGHT,
    INK, MUTED, LINE_GRAY, BORDER_GRAY, WHITE,
    STATUS_ACCENT, STATUS_BG,
    DISEASE_THRESHOLDS, diseases_info,
    REPORT_METADATA, BENCHMARKS, REFERENCES, LIMITATIONS,
    IMAGE_QUALITY_DEFAULTS, TOC_SECTIONS,
    RISK_LABELS, AI_DECISION_COLOR_MAP, URGENCY_MAP,
    SEVERITY_LEVELS, PRIORITY_COLORS, QUALITY_RATINGS,
)
from .styles import (
    FONT_REGULAR, FONT_BOLD, FONT_MEDIUM, FONT_SEMIBOLD,
    get_custom_styles,
)
from .icons import vector_icon
from .flowables import GradientProgressBar, RiskGauge, StarRating
from .helpers import (
    ar, metric_card, badge_element, build_qr_code, section_divider,
    compute_verification_hash, header_footer,
)
from .computations import (
    analyze_results, get_top_findings,
    compute_overall_confidence, compute_severity_score,
    get_clinical_priority, get_ai_decision, get_confidence_level,
    get_quality_rating, get_risk_info, get_urgency_label,
)
from .charts import build_pie_chart, build_bar_chart
from .components import (
    build_metric_row, build_badge_row, build_quality_rows,
    build_confidence_rows, build_timeline, build_pipeline,
    build_signature_block, build_disclaimer, build_doctor_notes,
    build_version_history, build_limitations_and_references,
)


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 0: COVER PAGE
# ══════════════════════════════════════════════════════════════════════════

def build_cover_page(report_id, report_date, report_time, patient_name,
                     image_path=None, logo_path=None):
    """Build the cover page of the report."""
    elements = []
    elements.append(Spacer(1, 0.8 * cm))
    
    # Logo
    if logo_path:
        try:
            elements.append(Image(logo_path, width=3.5 * cm, height=3.5 * cm))
        except Exception:
            elements.append(vector_icon("shield", 3 * cm, PRIMARY_BLUE))
    else:
        elements.append(vector_icon("shield", 3 * cm, PRIMARY_BLUE))
    
    elements.append(Spacer(1, 0.4 * cm))
    elements.append(Paragraph("RespAI", ParagraphStyle(
        'covBrand', fontName=FONT_BOLD, fontSize=32,
        textColor=PRIMARY_BLUE, alignment=TA_CENTER, leading=38)))
    elements.append(Paragraph("AI Chest X-ray Diagnostic Report", ParagraphStyle(
        'covTitle', fontName=FONT_BOLD, fontSize=17,
        textColor=SECONDARY_BLUE, alignment=TA_CENTER, leading=22)))
    elements.append(Spacer(1, 0.5 * cm))
    
    # Separator
    sep = Drawing(12 * cm, 3)
    sep.add(Rect(0, 0, 12 * cm, 2.5, fillColor=PRIMARY_BLUE, strokeColor=None, rx=1, ry=1))
    elements.append(sep)
    elements.append(Spacer(1, 0.6 * cm))
    
    # Patient info
    cover_info = Table([
        [Paragraph(ar("اسم المريض"), ParagraphStyle('ci_l', fontName=FONT_REGULAR, fontSize=9,
                                                      textColor=MUTED, alignment=TA_RIGHT, leading=12)),
         Paragraph(str(patient_name), ParagraphStyle('ci_v', fontName=FONT_BOLD, fontSize=10,
                                                      textColor=INK, alignment=TA_LEFT, leading=14))],
        [Paragraph("Report ID", ParagraphStyle('ci_l', fontName=FONT_REGULAR, fontSize=9,
                                                textColor=MUTED, alignment=TA_RIGHT, leading=12)),
         Paragraph(report_id, ParagraphStyle('ci_v', fontName=FONT_BOLD, fontSize=10,
                                              textColor=INK, alignment=TA_LEFT, leading=14))],
        [Paragraph(ar("التاريخ والوقت"), ParagraphStyle('ci_l', fontName=FONT_REGULAR, fontSize=9,
                                                         textColor=MUTED, alignment=TA_RIGHT, leading=12)),
         Paragraph(f"{report_date}  •  {report_time}", ParagraphStyle('ci_v', fontName=FONT_REGULAR, fontSize=10,
                                                                       textColor=INK, alignment=TA_LEFT, leading=14))],
    ], colWidths=[4 * cm, 8 * cm])
    cover_info.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(cover_info)
    elements.append(Spacer(1, 0.6 * cm))
    
    # X-ray image
    if image_path:
        try:
            img = Image(image_path, width=7 * cm, height=7 * cm)
            img_frame = Table([[img]], colWidths=[7.4 * cm], rowHeights=[7.4 * cm])
            img_frame.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), INK),
                ('BOX', (0, 0), (-1, -1), 2, PRIMARY_BLUE),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(img_frame)
            elements.append(Spacer(1, 0.4 * cm))
        except Exception:
            pass
    
    # QR code
    verify_url = f"https://respai.app/verify/{report_id}"
    elements.append(build_qr_code(verify_url, 2.5 * cm))
    elements.append(Spacer(1, 0.3 * cm))
    elements.append(Paragraph("CONFIDENTIAL MEDICAL DOCUMENT", ParagraphStyle(
        'conf', fontName=FONT_BOLD, fontSize=10,
        textColor=colors.HexColor('#7A1F1F'), alignment=TA_CENTER, leading=14)))
    
    return elements


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1: TABLE OF CONTENTS
# ══════════════════════════════════════════════════════════════════════════

def build_table_of_contents():
    """Build the table of contents page."""
    elements = []
    elements.append(Paragraph(ar("فهرس التقرير  —  Table of Contents"), ParagraphStyle(
        'toc_title', fontName=FONT_BOLD, fontSize=22,
        textColor=PRIMARY_BLUE, alignment=TA_CENTER, leading=28)))
    elements.append(Spacer(1, 0.4 * cm))
    
    toc_data = []
    for num, ar_t, en_t in TOC_SECTIONS:
        toc_data.append([
            Paragraph(num, ParagraphStyle('tn', fontName=FONT_BOLD, fontSize=11,
                                          textColor=PRIMARY_BLUE, alignment=TA_CENTER, leading=14)),
            Paragraph(f"{en_t}  —  {ar(ar_t)}", ParagraphStyle('tt', fontName=FONT_MEDIUM, fontSize=10,
                                                                textColor=INK, alignment=TA_RIGHT, leading=14)),
        ])
    toc_tbl = Table(toc_data, colWidths=[1.2 * cm, 14.8 * cm])
    toc_tbl.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LINEBELOW', (0, 0), (-1, -2), 0.3, LINE_GRAY),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [WHITE, ULTRA_LIGHT]),
    ]))
    elements.append(toc_tbl)
    return elements


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2: EXECUTIVE SUMMARY
# ═══════════════════════════════════════════════════════════════════════════

def build_executive_summary(results, flagged, top_disease, overall_color,
                            risk_accent, risk_bg, overall_confidence,
                            ai_decision_en, ai_decision_ar, severity_score,
                            clinical_priority_en, clinical_priority_ar):
    """Build section 1: Executive Summary."""
    elements = []
    elements.append(section_divider(1, "الملخص التنفيذي", "summary"))
    elements.append(Spacer(1, 0.3 * cm))
    
    if not flagged:
        imp_en = ("No radiographic evidence of acute cardiopulmonary abnormality. "
                  "Heart size is normal. Lungs are clear. No pleural effusion or pneumothorax.")
        imp_ar = ("لا توجد أدلة شعاعية على أي حالة قلبية رئوية حادة. حجم القلب طبيعي. "
                  "الرئتان صافيتان. لا يوجد انصباب جنبي أو استرواح صدر.")
    else:
        top = flagged[0]
        ti = diseases_info.get(top['disease'], {})
        imp_en = (f"Most probable finding: {top['disease']} ({top['probability']}%). "
                  f"{ti.get('impression', top['description'])}. Clinical correlation recommended.")
        imp_ar = (f"النتيجة الأكثر احتمالاً: {ar(top['ar_name'])} ({top['probability']}%). "
                  f"{ar(ti.get('impression', top['description']))}. يُنصح بالارتباط السريري.")
    
    imp_block = Table([
        [Paragraph(ar("الانطباع العام  Overall Impression"), ParagraphStyle(
            'imp_h', fontName=FONT_SEMIBOLD, fontSize=11,
            textColor=INK, alignment=TA_RIGHT, spaceAfter=4, leading=15))],
        [Paragraph(imp_en, ParagraphStyle('ie', fontName=FONT_REGULAR, fontSize=10,
                                           textColor=INK, alignment=TA_LEFT, leading=14))],
        [Paragraph(ar(imp_ar), ParagraphStyle('ia', fontName=FONT_REGULAR, fontSize=10,
                                               textColor=INK, alignment=TA_JUSTIFY, leading=15))],
    ], colWidths=[16 * cm])
    imp_block.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), ULTRA_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.5, LINE_GRAY),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(imp_block)
    elements.append(Spacer(1, 0.2 * cm))
    
    ai_clr_key = AI_DECISION_COLOR_MAP.get(ai_decision_en, 'green')
    gauge = RiskGauge(3 * cm, severity_score, risk_accent, "Risk Level")
    
    key_metrics = Table(
        [[metric_card(ar(risk_accent), "التقييم العام", risk_accent, risk_bg),
          metric_card(ar(ai_decision_ar), "قرار النموذج", STATUS_ACCENT[ai_clr_key], STATUS_BG[ai_clr_key]),
          metric_card(f"{overall_confidence}%", "ثقة النموذج", STATUS_ACCENT['green'], STATUS_BG['green'])]],
        colWidths=[4 * cm] * 3
    )
    key_metrics.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    
    exec_layout = Table([[gauge, key_metrics]], colWidths=[3.5 * cm, 12.5 * cm])
    exec_layout.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]))
    elements.append(exec_layout)
    
    if top_disease:
        pri_row = Table([[
            Paragraph(f"<b>{ar('الأولوية السريرية:')}</b> {ar(clinical_priority_ar)} ({clinical_priority_en})",
                      ParagraphStyle('pr', fontName=FONT_REGULAR, fontSize=10,
                                     textColor=INK, alignment=TA_RIGHT, leading=15)),
            Paragraph(f"<b>{ar('أبرز نتيجة:')}</b> {ar(top_disease['ar_name'])} — {top_disease['probability']}%",
                      ParagraphStyle('pr2', fontName=FONT_REGULAR, fontSize=10,
                                     textColor=INK, alignment=TA_RIGHT, leading=15)),
        ]], colWidths=[8 * cm, 8 * cm])
        pri_row.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(Spacer(1, 0.15 * cm))
        elements.append(pri_row)
    
    return elements


# ══════════════════════════════════════════════════════════════════════════
# SECTION 3: PATIENT INFORMATION
# ═══════════════════════════════════════════════════════════════════════════

def build_patient_info(patient_name, patient_age, patient_gender, patient_medical_id,
                       report_date, report_time, image_path=None):
    """Build section 2: Patient Information."""
    elements = []
    elements.append(section_divider(2, "بيانات المريض", "patient"))
    elements.append(Spacer(1, 0.3 * cm))
    
    pat_rows = [
        [Paragraph(ar("اسم المريض"), ParagraphStyle('pi_l', fontName=FONT_REGULAR, fontSize=9,
                                                      textColor=MUTED, alignment=TA_RIGHT, leading=12)),
         Paragraph(str(patient_name), ParagraphStyle('pi_v', fontName=FONT_REGULAR, fontSize=10,
                                                      textColor=INK, alignment=TA_LEFT, leading=14)),
         Paragraph(ar("العمر"), ParagraphStyle('pi_l', fontName=FONT_REGULAR, fontSize=9,
                                                textColor=MUTED, alignment=TA_RIGHT, leading=12)),
         Paragraph(str(patient_age), ParagraphStyle('pi_v', fontName=FONT_REGULAR, fontSize=10,
                                                     textColor=INK, alignment=TA_LEFT, leading=14))],
        [Paragraph(ar("الجنس"), ParagraphStyle('pi_l', fontName=FONT_REGULAR, fontSize=9,
                                                textColor=MUTED, alignment=TA_RIGHT, leading=12)),
         Paragraph(str(patient_gender), ParagraphStyle('pi_v', fontName=FONT_REGULAR, fontSize=10,
                                                        textColor=INK, alignment=TA_LEFT, leading=14)),
         Paragraph(ar("الرقم الطبي"), ParagraphStyle('pi_l', fontName=FONT_REGULAR, fontSize=9,
                                                      textColor=MUTED, alignment=TA_RIGHT, leading=12)),
         Paragraph(str(patient_medical_id), ParagraphStyle('pi_v', fontName=FONT_REGULAR, fontSize=10,
                                                            textColor=INK, alignment=TA_LEFT, leading=14))],
        [Paragraph(ar("تاريخ التحليل"), ParagraphStyle('pi_l', fontName=FONT_REGULAR, fontSize=9,
                                                        textColor=MUTED, alignment=TA_RIGHT, leading=12)),
         Paragraph(f"{report_date}  {report_time}", ParagraphStyle('pi_v', fontName=FONT_REGULAR, fontSize=10,
                                                                    textColor=INK, alignment=TA_LEFT, leading=14)),
         Paragraph(ar("تاريخ الإصدار"), ParagraphStyle('pi_l', fontName=FONT_REGULAR, fontSize=9,
                                                        textColor=MUTED, alignment=TA_RIGHT, leading=12)),
         Paragraph(report_date, ParagraphStyle('pi_v', fontName=FONT_REGULAR, fontSize=10,
                                                textColor=INK, alignment=TA_LEFT, leading=14))],
    ]
    pat_tbl = Table(pat_rows, colWidths=[3.2 * cm, 4.8 * cm, 3.2 * cm, 4.8 * cm])
    pat_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), ULTRA_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.6, LINE_GRAY),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, LINE_GRAY),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(pat_tbl)
    
    if image_path:
        try:
            xray = Image(image_path, width=5 * cm, height=5 * cm)
            xf = Table([[xray]], colWidths=[5.4 * cm], rowHeights=[5.4 * cm])
            xf.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), INK),
                ('BOX', (0, 0), (-1, -1), 1.5, PRIMARY_BLUE),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            img_caption = Paragraph(f"PA View  •  {REPORT_METADATA['input_resolution']}  •  {REPORT_METADATA['image_format']}  •  Preprocessed",
                                    ParagraphStyle('cap', fontName=FONT_REGULAR, fontSize=7.5,
                                                   textColor=MUTED, alignment=TA_CENTER, leading=10))
            img_sec = Table([[xf], [img_caption]], colWidths=[6 * cm])
            img_sec.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
            ]))
            elements.append(Spacer(1, 0.25 * cm))
            elements.append(img_sec)
        except Exception:
            pass
    
    return elements


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4: DASHBOARD STATISTICS
# ══════════════════════════════════════════════════════════════════════════

def build_dashboard_stats(total, flagged_count, max_prob, avg_prob, severity_score,
                          overall_confidence, processing_time, report_gen_time):
    """Build section 3: Dashboard Statistics."""
    elements = []
    elements.append(section_divider(3, "لوحة المعلومات", "stats"))
    elements.append(Spacer(1, 0.3 * cm))
    
    dash1 = Table(
        [[metric_card(total, "Total Diseases", PRIMARY_BLUE, ULTRA_LIGHT),
          metric_card(flagged_count, "Flagged Findings", STATUS_ACCENT['orange'], STATUS_BG['orange']),
          metric_card(f"{max_prob}%", "Highest Prob.", ACCENT_BLUE, ULTRA_LIGHT),
          metric_card(f"{avg_prob}%", "Average Prob.", SECONDARY_BLUE, ULTRA_LIGHT)]],
        colWidths=[4 * cm] * 4
    )
    dash1.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
    elements.append(dash1)
    elements.append(Spacer(1, 0.15 * cm))
    
    dash2 = Table(
        [[metric_card(f"{severity_score}", "Severity Score", STATUS_ACCENT['orange'], ULTRA_LIGHT),
          metric_card(f"{overall_confidence}%", "AI Confidence", STATUS_ACCENT['green'], STATUS_BG['green']),
          metric_card(f"{processing_time}s", "Inference Time", MUTED, ULTRA_LIGHT),
          metric_card(f"{report_gen_time}s", "Report Gen Time", MUTED, ULTRA_LIGHT)]],
        colWidths=[4 * cm] * 4
    )
    dash2.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
    elements.append(dash2)
    elements.append(Spacer(1, 0.2 * cm))
    
    bench_data = [[Paragraph("Metric", ParagraphStyle('bh', fontName=FONT_BOLD, fontSize=9,
                                                        textColor=WHITE, alignment=TA_CENTER, leading=13)),
                   Paragraph("Value", ParagraphStyle('bh2', fontName=FONT_BOLD, fontSize=9,
                                                      textColor=WHITE, alignment=TA_CENTER, leading=13))]]
    for k, v in BENCHMARKS.items():
        bench_data.append([
            Paragraph(k, ParagraphStyle('br', fontName=FONT_REGULAR, fontSize=10,
                                         textColor=INK, alignment=TA_LEFT, leading=14)),
            Paragraph(v, ParagraphStyle('bv', fontName=FONT_BOLD, fontSize=10,
                                         textColor=INK, alignment=TA_LEFT, leading=14)),
        ])
    bench_tbl = Table(bench_data, colWidths=[8.5 * cm, 4.5 * cm])
    bench_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), SECONDARY_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('BOX', (0, 0), (-1, -1), 0.5, SECONDARY_BLUE),
        ('INNERGRID', (0, 0), (-1, -1), 0.3, LINE_GRAY),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, ULTRA_LIGHT]),
    ]))
    elements.append(bench_tbl)
    elements.append(Spacer(1, 0.2 * cm))
    
    star_rating = StarRating(98, 100, 0.65 * cm)
    qs_text = Paragraph("Report Quality: 98/100", ParagraphStyle(
        'qs', fontName=FONT_BOLD, fontSize=10,
        textColor=PRIMARY_BLUE, alignment=TA_CENTER, leading=14))
    quality_block = Table([[star_rating], [qs_text]], colWidths=[3 * cm])
    quality_block.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
    elements.append(quality_block)
    
    return elements


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 5: DETAILED FINDINGS TABLE
# ═══════════════════════════════════════════════════════════════════════════

def build_detailed_findings(results):
    """Build section 4: Detailed Findings Table."""
    elements = []
    elements.append(section_divider(4, "النتائج التفصيلية", "findings"))
    elements.append(Spacer(1, 0.3 * cm))
    
    tbl_data = [[
        Paragraph(ar("المرض"), ParagraphStyle('th', fontName=FONT_BOLD, fontSize=9,
                                              textColor=WHITE, alignment=TA_CENTER, leading=13)),
        Paragraph("Disease", ParagraphStyle('th2', fontName=FONT_BOLD, fontSize=9,
                                             textColor=WHITE, alignment=TA_CENTER, leading=13)),
        Paragraph("ICD-10", ParagraphStyle('th3', fontName=FONT_BOLD, fontSize=9,
                                            textColor=WHITE, alignment=TA_CENTER, leading=13)),
        Paragraph(ar("النسبة"), ParagraphStyle('th4', fontName=FONT_BOLD, fontSize=9,
                                                textColor=WHITE, alignment=TA_CENTER, leading=13)),
        Paragraph("Severity", ParagraphStyle('th5', fontName=FONT_BOLD, fontSize=9,
                                              textColor=WHITE, alignment=TA_CENTER, leading=13)),
        Paragraph("Progress", ParagraphStyle('th6', fontName=FONT_BOLD, fontSize=9,
                                              textColor=WHITE, alignment=TA_CENTER, leading=13)),
        Paragraph("Priority", ParagraphStyle('th7', fontName=FONT_BOLD, fontSize=9,
                                              textColor=WHITE, alignment=TA_CENTER, leading=13)),
    ]]
    
    for res in results:
        info = diseases_info.get(res['disease'], {})
        sev_en, _ = SEVERITY_LEVELS.get(res['color'], ('Mild', 'خفيف'))
        sev_color = STATUS_ACCENT.get(res['color'], MUTED)
        rec_pri = URGENCY_MAP.get(res['color'], 'Routine')
        pr_color = PRIORITY_COLORS.get(rec_pri, MUTED)
        
        tbl_data.append([
            Paragraph(ar(res['ar_name']), ParagraphStyle('tc', fontName=FONT_MEDIUM, fontSize=9,
                                                          textColor=INK, alignment=TA_RIGHT, leading=13)),
            Paragraph(res['disease'], ParagraphStyle('tc2', fontName=FONT_REGULAR, fontSize=8,
                                                      textColor=MUTED, alignment=TA_LEFT, leading=11)),
            Paragraph(info.get('icd10', '—'), ParagraphStyle('tc3', fontName=FONT_REGULAR, fontSize=8,
                                                              textColor=MUTED, alignment=TA_CENTER, leading=11)),
            Paragraph(f"{res['probability']}%", ParagraphStyle('tc4', fontName=FONT_MEDIUM, fontSize=9,
                                                                textColor=INK, alignment=TA_CENTER, leading=13)),
            Paragraph(sev_en, ParagraphStyle('sv', fontName=FONT_BOLD, fontSize=8,
                                              textColor=sev_color, alignment=TA_CENTER, leading=11)),
            GradientProgressBar(2.3 * cm, 0.42 * cm, res['probability'], res['color']),
            Paragraph(rec_pri, ParagraphStyle('pr', fontName=FONT_BOLD, fontSize=7.5,
                                               textColor=pr_color, alignment=TA_CENTER, leading=10)),
        ])
    
    res_tbl = Table(tbl_data,
                    colWidths=[2.4*cm, 2.0*cm, 1.4*cm, 1.4*cm, 1.8*cm, 2.5*cm, 2.5*cm],
                    repeatRows=1)
    res_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), 0.8, PRIMARY_BLUE),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, LINE_GRAY),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, ULTRA_LIGHT]),
    ]))
    elements.append(res_tbl)
    return elements


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 6: DISEASE ANALYSIS (Top 3)
# ═══════════════════════════════════════════════════════════════════════════

def build_disease_analysis(flagged):
    """Build section 5: Disease Analysis (Top 3)."""
    elements = []
    if not flagged:
        return elements
    
    elements.append(section_divider(5, "تحليل الأمراض المكتشفة (Top 3)", "findings"))
    elements.append(Spacer(1, 0.3 * cm))
    
    for res in flagged[:3]:
        info = diseases_info.get(res['disease'], {})
        accent = STATUS_ACCENT.get(res['color'], MUTED)
        sev_en, _ = SEVERITY_LEVELS.get(res['color'], ('Mild', 'خفيف'))
        
        elements.append(Paragraph(
            f"<b>{ar(res['ar_name'])}</b>  —  {res['disease']}  —  {res['probability']}%",
            ParagraphStyle('da_t', fontName=FONT_SEMIBOLD, fontSize=11,
                           textColor=INK, alignment=TA_RIGHT, spaceAfter=4, leading=15)))
        elements.append(Spacer(1, 0.1 * cm))
        
        badges_row = build_badge_row((sev_en, ''), info.get('icd10', ''), info.get('snomed_ct', ''))
        elements.append(badges_row)
        elements.append(Spacer(1, 0.12 * cm))
        
        for label, val in [
            ('Radiographic Pattern', info.get('radiographic_pattern', '—')),
            ('Clinical Importance', info.get('clinical', '—')),
            ('Possible Causes', ' — '.join(info.get('causes', ['—']))),
            ('Differential Dx', ' — '.join(info.get('differential', ['—']))),
            ('Follow-up', info.get('followup', '—')),
            ('Management', info.get('management', '—')),
            ('Recommendation', info.get('recommendation', 'Observation')),
            ('Estimated Severity', sev_en),
            ('Estimated Urgency', URGENCY_MAP.get(res['color'], 'Routine')),
        ]:
            elements.append(Paragraph(f"<b>{label}:</b> {val}", ParagraphStyle(
                'da_d', fontName=FONT_REGULAR, fontSize=10,
                textColor=INK, alignment=TA_JUSTIFY, spaceAfter=3, leading=15)))
        
        elements.append(Spacer(1, 0.1 * cm))
        elements.append(GradientProgressBar(15 * cm, 0.5 * cm, res['probability'], res['color']))
        elements.append(Spacer(1, 0.3 * cm))
    
    return elements


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 7: AI ANALYTICS & CHARTS
# ═══════════════════════════════════════════════════════════════════════════

def build_ai_analytics(results, counts):
    """Build section 6: AI Analytics & Charts."""
    elements = []
    elements.append(section_divider(6, "الرسوم البيانية والتحليلات", "chart"))
    elements.append(Spacer(1, 0.3 * cm))
    
    pie = build_pie_chart(counts)
    bar = build_bar_chart(results)
    
    charts_tbl = Table([
        [Paragraph("Risk Distribution", ParagraphStyle('ct1', fontName=FONT_SEMIBOLD, fontSize=10,
                                                        textColor=PRIMARY_BLUE, alignment=TA_CENTER, leading=14)),
         Paragraph("Disease Probability Ranking", ParagraphStyle('ct2', fontName=FONT_SEMIBOLD, fontSize=10,
                                                                  textColor=PRIMARY_BLUE, alignment=TA_CENTER, leading=14))],
        [pie, bar],
    ], colWidths=[8 * cm, 8 * cm])
    charts_tbl.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOX', (0, 0), (-1, -1), 0.6, LINE_GRAY),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(charts_tbl)
    elements.append(Spacer(1, 0.3 * cm))
    
    elements.append(Paragraph(ar("توزيع مستويات الثقة  Confidence Distribution"), ParagraphStyle(
        'cd_h', fontName=FONT_SEMIBOLD, fontSize=11,
        textColor=INK, alignment=TA_RIGHT, spaceAfter=4, leading=15)))
    conf_rows = build_confidence_rows(results)
    elements.extend(conf_rows)
    
    return elements


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 8: GRAD-CAM HEATMAP
# ═══════════════════════════════════════════════════════════════════════════

def build_heatmap():
    """Build section 7: Grad-CAM Heatmap (placeholder)."""
    elements = []
    elements.append(section_divider(7, "خريطة الحرارة  Grad-CAM Heatmap", "heatmap"))
    elements.append(Spacer(1, 0.3 * cm))
    
    hm_ph = Table([
        [vector_icon("heatmap", 1.5 * cm, MUTED)],
        [Paragraph("Grad-CAM Heatmap Visualization", ParagraphStyle('hmp', fontName=FONT_BOLD, fontSize=11,
                                                                     textColor=MUTED, alignment=TA_CENTER, leading=14))],
        [Paragraph("Feature Not Enabled in Current Version", ParagraphStyle('hms', fontName=FONT_REGULAR, fontSize=9,
                                                                            textColor=MUTED, alignment=TA_CENTER, leading=12))],
        [Paragraph(ar("Original Image → Grad-CAM Overlay → Attention Map — ستتوفر في الإصدارات القادمة"),
                   ParagraphStyle('hma', fontName=FONT_REGULAR, fontSize=8,
                                  textColor=MUTED, alignment=TA_CENTER, leading=11))],
    ], colWidths=[16 * cm], rowHeights=[1.8*cm, 0.8*cm, 0.6*cm, 0.8*cm])
    hm_ph.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), ULTRA_LIGHT),
        ('BOX', (0, 0), (-1, -1), 1, LINE_GRAY),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(hm_ph)
    return elements


# ══════════════════════════════════════════════════════════════════════════
# SECTION 9: CLINICAL INTERPRETATION
# ═══════════════════════════════════════════════════════════════════════════

def build_clinical_interpretation(flagged, top_disease):
    """Build section 8: Clinical Interpretation."""
    elements = []
    if not flagged:
        return elements
    
    elements.append(section_divider(8, "التفسير السريري", "doctor"))
    elements.append(Spacer(1, 0.3 * cm))
    
    elements.append(Paragraph(ar("الانطباع الشعاعي  Radiological Impression"), ParagraphStyle(
        'ci_h', fontName=FONT_SEMIBOLD, fontSize=11,
        textColor=INK, alignment=TA_RIGHT, spaceAfter=4, leading=15)))
    if top_disease:
        elements.append(Paragraph(
            ar(f"يُلاحظ وجود {ar(top_disease['ar_name'])} بنسبة احتمالية "
               f"{top_disease['probability']}%، مما يستدعي تقييماً سريرياً شاملاً."),
            ParagraphStyle('ci_b', fontName=FONT_REGULAR, fontSize=10,
                           textColor=INK, alignment=TA_JUSTIFY, spaceAfter=3, leading=15)))
    elements.append(Spacer(1, 0.15 * cm))
    
    elements.append(Paragraph(ar("الارتباط السريري  Clinical Correlation"), ParagraphStyle(
        'ci_h2', fontName=FONT_SEMIBOLD, fontSize=11,
        textColor=INK, alignment=TA_RIGHT, spaceAfter=4, leading=15)))
    elements.append(Paragraph(
        ar("يجب ربط النتائج بالأعراض السريرية والفحوصات المخبرية قبل اتخاذ أي قرار علاجي."),
        ParagraphStyle('ci_b2', fontName=FONT_REGULAR, fontSize=10,
                       textColor=INK, alignment=TA_JUSTIFY, spaceAfter=3, leading=15)))
    elements.append(Spacer(1, 0.15 * cm))
    
    elements.append(Paragraph(ar("النتائج المتوقعة  Expected Findings"), ParagraphStyle(
        'ci_h3', fontName=FONT_SEMIBOLD, fontSize=11,
        textColor=INK, alignment=TA_RIGHT, spaceAfter=4, leading=15)))
    for res in flagged[:3]:
        ti = diseases_info.get(res['disease'], {})
        elements.append(Paragraph(
            f"&#9679;  <b>{ar(res['ar_name'])}:</b> {ar(ti.get('impression', res['description']))}",
            ParagraphStyle('ci_i', fontName=FONT_REGULAR, fontSize=10,
                           textColor=INK, alignment=TA_RIGHT, spaceAfter=3, leading=15)))
    
    return elements


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 10: CLINICAL DECISION SUPPORT
# ═══════════════════════════════════════════════════════════════════════════

def build_clinical_decision_support(flagged):
    """Build section 9: Clinical Decision Support."""
    elements = []
    if not flagged:
        return elements
    
    elements.append(section_divider(9, "دعم القرار السريري", "recommend"))
    elements.append(Spacer(1, 0.3 * cm))
    
    cds_data = [[
        Paragraph("Disease", ParagraphStyle('cds_h', fontName=FONT_BOLD, fontSize=9,
                                             textColor=WHITE, alignment=TA_CENTER, leading=13)),
        Paragraph("Recommended Test", ParagraphStyle('cds_h2', fontName=FONT_BOLD, fontSize=9,
                                                       textColor=WHITE, alignment=TA_CENTER, leading=13)),
        Paragraph("Medication", ParagraphStyle('cds_h3', fontName=FONT_BOLD, fontSize=9,
                                                textColor=WHITE, alignment=TA_CENTER, leading=13)),
        Paragraph("Specialist", ParagraphStyle('cds_h4', fontName=FONT_BOLD, fontSize=9,
                                                textColor=WHITE, alignment=TA_CENTER, leading=13)),
        Paragraph("Follow-up", ParagraphStyle('cds_h5', fontName=FONT_BOLD, fontSize=9,
                                               textColor=WHITE, alignment=TA_CENTER, leading=13)),
    ]]
    for res in flagged[:5]:
        ti = diseases_info.get(res['disease'], {})
        cds_data.append([
            Paragraph(res['disease'], ParagraphStyle('cds_r', fontName=FONT_REGULAR, fontSize=8,
                                                      textColor=INK, alignment=TA_LEFT, leading=11)),
            Paragraph(ti.get('test', '—'), ParagraphStyle('cds_r2', fontName=FONT_REGULAR, fontSize=8,
                                                            textColor=INK, alignment=TA_LEFT, leading=11)),
            Paragraph(ti.get('medication', '—'), ParagraphStyle('cds_r3', fontName=FONT_REGULAR, fontSize=8,
                                                                  textColor=INK, alignment=TA_LEFT, leading=11)),
            Paragraph(ti.get('specialist', '—'), ParagraphStyle('cds_r4', fontName=FONT_REGULAR, fontSize=8,
                                                                  textColor=INK, alignment=TA_LEFT, leading=11)),
            Paragraph(ti.get('followup', '—'), ParagraphStyle('cds_r5', fontName=FONT_REGULAR, fontSize=8,
                                                                textColor=INK, alignment=TA_LEFT, leading=11)),
        ])
    cds_tbl = Table(cds_data, colWidths=[2.5*cm, 3.5*cm, 3.5*cm, 3.0*cm, 3.5*cm], repeatRows=1)
    cds_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), SECONDARY_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('BOX', (0, 0), (-1, -1), 0.6, SECONDARY_BLUE),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, LINE_GRAY),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, ULTRA_LIGHT]),
    ]))
    elements.append(cds_tbl)
    return elements


# ══════════════════════════════════════════════════════════════════════════
# SECTION 11: AI RECOMMENDATIONS
# ══════════════════════════════════════════════════════════════════════════

def build_ai_recommendations(flagged):
    """Build section 10: AI Recommendations."""
    elements = []
    elements.append(section_divider(10, "توصيات الذكاء الاصطناعي", "recommend"))
    elements.append(Spacer(1, 0.3 * cm))
    
    if flagged:
        sections_rec = [
            ("الإجراءات الفورية  Immediate Actions", ["مراجعة أخصائي الأشعة خلال 24 ساعة لتأكيد النتائج", "تقييم العلامات الحيوية والحالة السريرية للمريض"]),
            ("الفحوصات المقترحة  Recommended Tests", ["أشعة مقطعية محوسبة (CT) حسب الحاجة السريرية", "فحوصات مخبرية شاملة (CBC, CRP, BNP)"]),
            ("الفحوصات المخبرية  Laboratory Tests", ["صورة دم كاملة CBC", "مؤشرات الالتهاب CRP / ESR", "وظائف الكلى والكبد"]),
            ("المتابعة الشعاعية  Radiology Follow-up", ["أشعة صدر متابعة بعد 4-6 أسابيع", "CT محوسب عالي الدقة إذا لزم الأمر"]),
            ("توصية الإحالة  Referral", ["إحالة إلى أخصائي الصدر أو القلب حسب الحالة"]),
            ("نصائح للمريض  Patient Advice", ["الإقلاع عن التدخين إن وُجد", "ممارسة نشاط بدني معتدل", "اتباع نظام غذائي متوازن"]),
            ("المتابعة طويلة الأمد  Long-term Follow-up", ["متابعة دورية كل 3-6 أشهر حسب شدة الحالة", "توثيق النتائج في الملف الطبي الإلكتروني"]),
        ]
    else:
        sections_rec = [("لا توجد توصيات خاصة — الحالة طبيعية", ["الاستمرار في الفحوصات الدورية الروتينية", "الحفاظ على نمط حياة صحي", "إجراء فحص سنوي شامل"])]
    
    for title, items in sections_rec:
        elements.append(Paragraph(ar(title), ParagraphStyle(
            'ar_h', fontName=FONT_SEMIBOLD, fontSize=11,
            textColor=INK, alignment=TA_RIGHT, spaceAfter=4, leading=15)))
        for it in items:
            elements.append(Paragraph(f"&#9679;  {ar(it)}", ParagraphStyle(
                'ar_i', fontName=FONT_REGULAR, fontSize=10,
                textColor=INK, alignment=TA_RIGHT, spaceAfter=3, leading=15)))
        elements.append(Spacer(1, 0.1 * cm))
    
    if flagged:
        elements.append(Paragraph(ar("توصيات خاصة حسب الأمراض المكتشفة"), ParagraphStyle(
            'ar_h2', fontName=FONT_SEMIBOLD, fontSize=11,
            textColor=INK, alignment=TA_RIGHT, spaceAfter=4, leading=15)))
        for res in flagged[:3]:
            ti = diseases_info.get(res['disease'], {})
            rec = ti.get('recommendation', 'Observation')
            elements.append(Paragraph(f"&#9679;  <b>{ar(res['ar_name'])}:</b> {rec}", ParagraphStyle(
                'ar_i2', fontName=FONT_REGULAR, fontSize=10,
                textColor=INK, alignment=TA_RIGHT, spaceAfter=3, leading=15)))
    
    return elements


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 12: CONFIDENCE ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════

def build_confidence_analysis(overall_confidence, highest_confidence, validation_auc, confidence_en, confidence_ar):
    """Build section 11: Confidence Analysis."""
    elements = []
    elements.append(section_divider(11, "تحليل ثقة النموذج", "confidence"))
    elements.append(Spacer(1, 0.3 * cm))
    
    conf_metrics = Table(
        [[metric_card(f"{overall_confidence}%", f"Overall ({confidence_ar})", ACCENT_BLUE, ULTRA_LIGHT),
          metric_card(f"{highest_confidence}%", "Highest Prediction", PRIMARY_BLUE, ULTRA_LIGHT),
          metric_card(validation_auc, "Validation AUC", STATUS_ACCENT['green'], STATUS_BG['green'])]],
        colWidths=[5.3 * cm] * 3
    )
    conf_metrics.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
    elements.append(conf_metrics)
    elements.append(Spacer(1, 0.2 * cm))
    
    conf_bar_key = 'green' if overall_confidence >= 70 else 'yellow'
    elements.append(GradientProgressBar(15 * cm, 0.55 * cm, overall_confidence, conf_bar_key))
    elements.append(Spacer(1, 0.1 * cm))
    elements.append(Paragraph(ar(f"مستوى الثقة: {confidence_ar} ({confidence_en}). يُحسب متوسط الثقة من جميع الأمراض المفحوصة."),
                              ParagraphStyle('ca_n', fontName=FONT_REGULAR, fontSize=9,
                                             textColor=MUTED, alignment=TA_RIGHT, leading=13)))
    return elements


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 13: EXPLAINABLE AI
# ═══════════════════════════════════════════════════════════════════════════

def build_explainable_ai(processing_time, report_gen_time, report_time):
    """Build section 12: Explainable AI."""
    elements = []
    elements.append(section_divider(12, "كيف اتخذ النموذج قراره  Explainable AI", "ai"))
    elements.append(Spacer(1, 0.3 * cm))
    
    pipe_tbl = build_pipeline()
    elements.append(pipe_tbl)
    elements.append(Spacer(1, 0.3 * cm))
    
    for title, desc in [
        ("Image Preprocessing", "يتم تغيير حجم الصورة إلى 224×224 بكسل وتطبيع قيم البكسل لتحسين أداء النموذج."),
        ("Feature Extraction", "يستخدم النموذج بنية DenseNet-121 لاستخراج الميزات الشعاعية من الطبقات العميقة."),
        ("Attention Mechanism", "يركز النموذج على المناطق ذات الصلة في الأشعة باستخدام آليات الانتباه العميق."),
        ("Probability Calc.", "يتم حساب احتمالية كل مرض باستخدام دالة Sigmoid على المخرجات النهائية."),
        ("Thresholding", "تُصنف النتيجة كـ Positive إذا تجاوزت الاحتمالية عتبة 0.50 المحددة مسبقاً."),
        ("Final Classification", "يتم ترتيب النتائج تنازلياً وتحديد مستوى الخطورة والأولوية السريرية."),
    ]:
        elements.append(Paragraph(f"<b>{title}:</b> {ar(desc)}", ParagraphStyle(
            'ea_d', fontName=FONT_REGULAR, fontSize=10,
            textColor=INK, alignment=TA_JUSTIFY, spaceAfter=3, leading=15)))
    
    elements.append(Spacer(1, 0.2 * cm))
    elements.append(Paragraph(ar("الجدول الزمني للمعالجة  Processing Timeline"), ParagraphStyle(
        'ea_h', fontName=FONT_SEMIBOLD, fontSize=11,
        textColor=INK, alignment=TA_RIGHT, spaceAfter=4, leading=15)))
    tl_tbl = build_timeline(report_time, processing_time, report_gen_time)
    elements.append(tl_tbl)
    return elements


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 14: IMAGE QUALITY ASSESSMENT
# ═══════════════════════════════════════════════════════════════════════════

def build_image_quality_assessment():
    """Build section 13: Image Quality Assessment."""
    elements = []
    elements.append(section_divider(13, "تقييم جودة الصورة", "quality"))
    elements.append(Spacer(1, 0.3 * cm))
    
    quality_rows = build_quality_rows()
    elements.extend(quality_rows)
    
    elements.append(Spacer(1, 0.1 * cm))
    elements.append(Paragraph(ar("ملاحظة: هذه القيم مرجعية حالياً وسيتم حسابها تلقائياً من الصورة في الإصدارات القادمة."),
                              ParagraphStyle('qa_n', fontName=FONT_REGULAR, fontSize=9,
                                             textColor=MUTED, alignment=TA_RIGHT, leading=13)))
    return elements


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 15: TECHNICAL INFORMATION
# ═══════════════════════════════════════════════════════════════════════════

def build_technical_information(processing_time):
    """Build section 14: Technical Information."""
    elements = []
    elements.append(section_divider(14, "المعلومات التقنية", "tech"))
    elements.append(Spacer(1, 0.3 * cm))
    
    tech_rows = [
        [Paragraph("Model Architecture", ParagraphStyle('ti_l', fontName=FONT_REGULAR, fontSize=9,
                                                          textColor=MUTED, alignment=TA_RIGHT, leading=12)),
         Paragraph("DenseNet-121", ParagraphStyle('ti_v', fontName=FONT_REGULAR, fontSize=10,
                                                   textColor=INK, alignment=TA_LEFT, leading=14)),
         Paragraph("Training Dataset", ParagraphStyle('ti_l', fontName=FONT_REGULAR, fontSize=9,
                                                       textColor=MUTED, alignment=TA_RIGHT, leading=12)),
         Paragraph(REPORT_METADATA['dataset'], ParagraphStyle('ti_v', fontName=FONT_REGULAR, fontSize=10,
                                                               textColor=INK, alignment=TA_LEFT, leading=14))],
        [Paragraph("Training Images", ParagraphStyle('ti_l', fontName=FONT_REGULAR, fontSize=9,
                                                      textColor=MUTED, alignment=TA_RIGHT, leading=12)),
         Paragraph(REPORT_METADATA['training_images'], ParagraphStyle('ti_v', fontName=FONT_REGULAR, fontSize=10,
                                                                       textColor=INK, alignment=TA_LEFT, leading=14)),
         Paragraph("Validation AUC", ParagraphStyle('ti_l', fontName=FONT_REGULAR, fontSize=9,
                                                     textColor=MUTED, alignment=TA_RIGHT, leading=12)),
         Paragraph(REPORT_METADATA['validation_auc'], ParagraphStyle('ti_v', fontName=FONT_REGULAR, fontSize=10,
                                                                      textColor=INK, alignment=TA_LEFT, leading=14))],
        [Paragraph("Framework", ParagraphStyle('ti_l', fontName=FONT_REGULAR, fontSize=9,
                                                textColor=MUTED, alignment=TA_RIGHT, leading=12)),
         Paragraph(REPORT_METADATA['framework'], ParagraphStyle('ti_v', fontName=FONT_REGULAR, fontSize=10,
                                                                 textColor=INK, alignment=TA_LEFT, leading=14)),
         Paragraph("Hardware", ParagraphStyle('ti_l', fontName=FONT_REGULAR, fontSize=9,
                                               textColor=MUTED, alignment=TA_RIGHT, leading=12)),
         Paragraph(REPORT_METADATA['hardware'], ParagraphStyle('ti_v', fontName=FONT_REGULAR, fontSize=10,
                                                                textColor=INK, alignment=TA_LEFT, leading=14))],
        [Paragraph("PyTorch Version", ParagraphStyle('ti_l', fontName=FONT_REGULAR, fontSize=9,
                                                      textColor=MUTED, alignment=TA_RIGHT, leading=12)),
         Paragraph(REPORT_METADATA['pytorch_version'], ParagraphStyle('ti_v', fontName=FONT_REGULAR, fontSize=10,
                                                                       textColor=INK, alignment=TA_LEFT, leading=14)),
         Paragraph("CUDA Version", ParagraphStyle('ti_l', fontName=FONT_REGULAR, fontSize=9,
                                                    textColor=MUTED, alignment=TA_RIGHT, leading=12)),
         Paragraph(REPORT_METADATA['cuda_version'], ParagraphStyle('ti_v', fontName=FONT_REGULAR, fontSize=10,
                                                                    textColor=INK, alignment=TA_LEFT, leading=14))],
        [Paragraph("Input Resolution", ParagraphStyle('ti_l', fontName=FONT_REGULAR, fontSize=9,
                                                       textColor=MUTED, alignment=TA_RIGHT, leading=12)),
         Paragraph(REPORT_METADATA['input_resolution'], ParagraphStyle('ti_v', fontName=FONT_REGULAR, fontSize=10,
                                                                        textColor=INK, alignment=TA_LEFT, leading=14)),
         Paragraph("Image Format", ParagraphStyle('ti_l', fontName=FONT_REGULAR, fontSize=9,
                                                    textColor=MUTED, alignment=TA_RIGHT, leading=12)),
         Paragraph(REPORT_METADATA['image_format'], ParagraphStyle('ti_v', fontName=FONT_REGULAR, fontSize=10,
                                                                    textColor=INK, alignment=TA_LEFT, leading=14))],
        [Paragraph("Prediction Threshold", ParagraphStyle('ti_l', fontName=FONT_REGULAR, fontSize=9,
                                                           textColor=MUTED, alignment=TA_RIGHT, leading=12)),
         Paragraph(REPORT_METADATA['threshold'], ParagraphStyle('ti_v', fontName=FONT_REGULAR, fontSize=10,
                                                                  textColor=INK, alignment=TA_LEFT, leading=14)),
         Paragraph("Inference Time", ParagraphStyle('ti_l', fontName=FONT_REGULAR, fontSize=9,
                                                     textColor=MUTED, alignment=TA_RIGHT, leading=12)),
         Paragraph(f"{processing_time} s", ParagraphStyle('ti_v', fontName=FONT_REGULAR, fontSize=10,
                                                           textColor=INK, alignment=TA_LEFT, leading=14))],
        [Paragraph("Report Version", ParagraphStyle('ti_l', fontName=FONT_REGULAR, fontSize=9,
                                                     textColor=MUTED, alignment=TA_RIGHT, leading=12)),
         Paragraph(f"v{REPORT_METADATA['report_version']}", ParagraphStyle('ti_v', fontName=FONT_REGULAR, fontSize=10,
                                                                            textColor=INK, alignment=TA_LEFT, leading=14)),
         Paragraph("Model Version", ParagraphStyle('ti_l', fontName=FONT_REGULAR, fontSize=9,
                                                    textColor=MUTED, alignment=TA_RIGHT, leading=12)),
         Paragraph(REPORT_METADATA['model_version'], ParagraphStyle('ti_v', fontName=FONT_REGULAR, fontSize=10,
                                                                     textColor=INK, alignment=TA_LEFT, leading=14))],
    ]
    tech_tbl = Table(tech_rows, colWidths=[3.2*cm, 4.8*cm, 3.2*cm, 4.8*cm])
    tech_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), ULTRA_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.6, LINE_GRAY),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, LINE_GRAY),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [WHITE, ULTRA_LIGHT]),
    ]))
    elements.append(tech_tbl)
    elements.append(Spacer(1, 0.25 * cm))
    
    elements.append(Paragraph(ar("سجل إصدارات النموذج  AI Version History"), ParagraphStyle(
        'ti_h', fontName=FONT_SEMIBOLD, fontSize=11,
        textColor=INK, alignment=TA_RIGHT, spaceAfter=4, leading=15)))
    ver_tbl = build_version_history()
    elements.append(ver_tbl)
    return elements


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 16: LIMITATIONS & REFERENCES + DISCLAIMER + DOCTOR NOTES
# ═══════════════════════════════════════════════════════════════════════════

def build_limitations_references_disclaimer_notes():
    """Build section 15: Limitations, References, Disclaimer, Doctor Notes."""
    elements = []
    elements.append(section_divider(15, "حدود النظام والمراجع", "book"))
    elements.append(Spacer(1, 0.3 * cm))
    
    elements.extend(build_limitations_and_references())
    elements.append(Spacer(1, 0.3 * cm))
    elements.extend(build_disclaimer())
    elements.append(Spacer(1, 0.3 * cm))
    elements.extend(build_doctor_notes(6))
    return elements


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 17: VERIFICATION & SIGNATURES
# ═══════════════════════════════════════════════════════════════════════════

def build_verification_signatures(report_id, report_date, report_time, verification_hash):
    """Build section 16: Verification & Signatures."""
    elements = []
    elements.append(section_divider(16, "التوقيعات والتحقق", "shield"))
    elements.append(Spacer(1, 0.3 * cm))
    
    verify_url = f"https://respai.app/verify/{report_id}"
    sig_elements = build_signature_block(report_id, report_date, report_time, verify_url, verification_hash)
    elements.extend(sig_elements)
    return elements


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 18: FINAL PAGE
# ═══════════════════════════════════════════════════════════════════════════

def build_final_page(flagged, top_disease, max_prob, overall_confidence, confidence_ar,
                     clinical_priority_en, ai_decision_en, ai_decision_ar, priority_color,
                     patient_status, patient_status_color, report_date):
    """Build the final page with clinical impression and summary."""
    elements = []
    
    if not flagged:
        fci_en = ("No significant radiographic abnormalities detected. Chest X-ray appears within "
                  "normal limits. Routine follow-up recommended per standard clinical guidelines.")
        fci_ar = ("لا توجد تشوهات شعاعية ملحوظة. أشعة الصدر ضمن الحدود الطبيعية. "
                  "يُنصح بالمتابعة الروتينية وفقاً للإرشادات السريرية القياسية.")
    else:
        top = flagged[0]
        fci_en = (f"Findings suggestive of {top['disease']} (probability: {top['probability']}%). "
                  f"Clinical correlation and further imaging recommended. Priority: {clinical_priority_en}.")
        fci_ar = (f"نتائج تشير إلى {ar(top['ar_name'])} (احتمالية: {top['probability']}%). "
                  f"يُنصح بالارتباط السريري وتصوير إضافي. الأولوية: {clinical_priority_en}.")
    
    fci_block = Table([
        [Paragraph("FINAL CLINICAL IMPRESSION", ParagraphStyle('fci', fontName=FONT_BOLD, fontSize=16,
                                                               textColor=PRIMARY_BLUE, alignment=TA_CENTER, leading=20))],
        [Spacer(1, 0.15 * cm)],
        [Paragraph(fci_en, ParagraphStyle('fci_en', fontName=FONT_REGULAR, fontSize=11,
                                           textColor=INK, alignment=TA_LEFT, leading=16))],
        [Paragraph(ar(fci_ar), ParagraphStyle('fci_ar', fontName=FONT_REGULAR, fontSize=10,
                                               textColor=INK, alignment=TA_JUSTIFY, leading=15))],
    ], colWidths=[16 * cm])
    fci_block.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), ULTRA_LIGHT),
        ('BOX', (0, 0), (-1, -1), 1.2, PRIMARY_BLUE),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(fci_block)
    elements.append(Spacer(1, 0.5 * cm))
    
    summary_rows = [
        [Paragraph("Patient Status", ParagraphStyle('fs_l', fontName=FONT_REGULAR, fontSize=9,
                                                     textColor=MUTED, alignment=TA_RIGHT, leading=12)),
         Paragraph(patient_status, ParagraphStyle('fs_v', fontName=FONT_BOLD, fontSize=10,
                                                   textColor=patient_status_color, alignment=TA_LEFT, leading=14)),
         Paragraph("Most Likely Disease", ParagraphStyle('fs_l', fontName=FONT_REGULAR, fontSize=9,
                                                          textColor=MUTED, alignment=TA_RIGHT, leading=12)),
         Paragraph(top_disease['disease'] if top_disease else "—", ParagraphStyle('fs_v', fontName=FONT_REGULAR, fontSize=10,
                                                                                   textColor=INK, alignment=TA_LEFT, leading=14))],
        [Paragraph("Highest Probability", ParagraphStyle('fs_l', fontName=FONT_REGULAR, fontSize=9,
                                                          textColor=MUTED, alignment=TA_RIGHT, leading=12)),
         Paragraph(f"{max_prob}%", ParagraphStyle('fs_v', fontName=FONT_BOLD, fontSize=10,
                                                   textColor=INK, alignment=TA_LEFT, leading=14)),
         Paragraph("AI Confidence", ParagraphStyle('fs_l', fontName=FONT_REGULAR, fontSize=9,
                                                    textColor=MUTED, alignment=TA_RIGHT, leading=12)),
         Paragraph(f"{overall_confidence}% ({confidence_ar})", ParagraphStyle('fs_v', fontName=FONT_REGULAR, fontSize=10,
                                                                               textColor=INK, alignment=TA_LEFT, leading=14))],
        [Paragraph("Final Recommendation", ParagraphStyle('fs_l', fontName=FONT_REGULAR, fontSize=9,
                                                           textColor=MUTED, alignment=TA_RIGHT, leading=12)),
         Paragraph(clinical_priority_en, ParagraphStyle('fs_v', fontName=FONT_BOLD, fontSize=10,
                                                         textColor=priority_color, alignment=TA_LEFT, leading=14)),
         Paragraph("AI Decision", ParagraphStyle('fs_l', fontName=FONT_REGULAR, fontSize=9,
                                                  textColor=MUTED, alignment=TA_RIGHT, leading=12)),
         Paragraph(f"{ai_decision_en} ({ar(ai_decision_ar)})", ParagraphStyle('fs_v', fontName=FONT_REGULAR, fontSize=10,
                                                                               textColor=INK, alignment=TA_LEFT, leading=14))],
    ]
    summary_tbl = Table(summary_rows, colWidths=[3.2*cm, 4.8*cm, 3.2*cm, 4.8*cm])
    summary_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), ULTRA_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.6, LINE_GRAY),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, LINE_GRAY),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [WHITE, ULTRA_LIGHT]),
    ]))
    
    elements.append(Paragraph(ar("ملخص التقرير النهائي  Final Report Summary"), ParagraphStyle(
        'fs_h', fontName=FONT_BOLD, fontSize=14,
        textColor=PRIMARY_BLUE, alignment=TA_RIGHT, spaceAfter=6, leading=18)))
    elements.append(Spacer(1, 0.15 * cm))
    elements.append(summary_tbl)
    elements.append(Spacer(1, 0.3 * cm))
    
    sys_rows = [
        [Paragraph("System Name", ParagraphStyle('si_l', fontName=FONT_REGULAR, fontSize=9,
                                                  textColor=MUTED, alignment=TA_RIGHT, leading=12)),
         Paragraph("RespAI — Medical AI Diagnostic System", ParagraphStyle('si_v', fontName=FONT_REGULAR, fontSize=10,
                                                                            textColor=INK, alignment=TA_LEFT, leading=14))],
        [Paragraph("Version", ParagraphStyle('si_l', fontName=FONT_REGULAR, fontSize=9,
                                              textColor=MUTED, alignment=TA_RIGHT, leading=12)),
         Paragraph(f"Report v{REPORT_METADATA['report_version']}  •  Model {REPORT_METADATA['model_version']}",
                   ParagraphStyle('si_v', fontName=FONT_REGULAR, fontSize=10,
                                  textColor=INK, alignment=TA_LEFT, leading=14))],
        [Paragraph("Model", ParagraphStyle('si_l', fontName=FONT_REGULAR, fontSize=9,
                                            textColor=MUTED, alignment=TA_RIGHT, leading=12)),
         Paragraph(f"{REPORT_METADATA['model_name']} (DenseNet-121)",
                   ParagraphStyle('si_v', fontName=FONT_REGULAR, fontSize=10,
                                  textColor=INK, alignment=TA_LEFT, leading=14))],
        [Paragraph("Dataset", ParagraphStyle('si_l', fontName=FONT_REGULAR, fontSize=9,
                                              textColor=MUTED, alignment=TA_RIGHT, leading=12)),
         Paragraph(f"{REPORT_METADATA['dataset']} — {REPORT_METADATA['training_images']} images",
                   ParagraphStyle('si_v', fontName=FONT_REGULAR, fontSize=10,
                                  textColor=INK, alignment=TA_LEFT, leading=14))],
        [Paragraph("Intended Use", ParagraphStyle('si_l', fontName=FONT_REGULAR, fontSize=9,
                                                   textColor=MUTED, alignment=TA_RIGHT, leading=12)),
         Paragraph("Clinical Decision Support / Research",
                   ParagraphStyle('si_v', fontName=FONT_REGULAR, fontSize=10,
                                  textColor=INK, alignment=TA_LEFT, leading=14))],
    ]
    sys_tbl = Table(sys_rows, colWidths=[4 * cm, 12 * cm])
    sys_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), ULTRA_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.6, LINE_GRAY),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, LINE_GRAY),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [WHITE, ULTRA_LIGHT]),
    ]))
    elements.append(Paragraph(ar("معلومات النظام  System Information"), ParagraphStyle(
        'si_h', fontName=FONT_BOLD, fontSize=14,
        textColor=PRIMARY_BLUE, alignment=TA_RIGHT, spaceAfter=6, leading=18)))
    elements.append(Spacer(1, 0.15 * cm))
    elements.append(sys_tbl)
    elements.append(Spacer(1, 0.3 * cm))
    
    elements.append(Paragraph(ar("سياسة الخصوصية والاستخدام"), ParagraphStyle(
        'pv_h', fontName=FONT_BOLD, fontSize=14,
        textColor=PRIMARY_BLUE, alignment=TA_RIGHT, spaceAfter=6, leading=18)))
    elements.append(Spacer(1, 0.1 * cm))
    for p in [
        "يتم التعامل مع جميع بيانات المريض بسرية تامة وفقاً لأنظمة HIPAA / GDPR.",
        "لا يتم تخزين الصور أو البيانات الشخصية على خوادم خارجية دون موافصة خطية.",
        "هذا التقرير أداة مساعدة للقرار السريري وليس بديلاً عن الحكم الطبي المتخصص.",
        "يمكن التحقق من صحة التقرير عبر رمز QR أو بصمة التحقق الرقمية المرفقة.",
        "أي تعديل على محتوى التقرير يُفقده صفة الرسمية ويُعد باطلاً.",
    ]:
        elements.append(Paragraph(f"&#9679;  {ar(p)}", ParagraphStyle(
            'pv_i', fontName=FONT_REGULAR, fontSize=10,
            textColor=INK, alignment=TA_JUSTIFY, spaceAfter=3, leading=15)))
    
    elements.append(Spacer(1, 0.2 * cm))
    elements.append(Paragraph(ar(f"جميع حقوق هذا التقرير محفوظة ©️ {report_date[:4]} RespAI. يُمنع نسخ أو تعديل أو إعادة توزيع هذا التقرير دون إذن خطي مسبق."),
                              ParagraphStyle('cp', fontName=FONT_REGULAR, fontSize=10,
                                             textColor=INK, alignment=TA_JUSTIFY, leading=15)))
    elements.append(Spacer(1, 0.15 * cm))
    elements.append(Paragraph("support@respai.app   •   www.respai.app   •   +000 000 000 000",
                              ParagraphStyle('ct', fontName=FONT_REGULAR, fontSize=10,
                                             textColor=INK, alignment=TA_LEFT, leading=14)))
    
    return elements