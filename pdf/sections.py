"""
PDF Report Sections Builder (HTML version)
=============================================

This module contains functions to build each of the report sections.
Each function returns an HTML string to be inserted into the final document
(instead of a list of ReportLab flowables).

Dependencies:
- All other pdf modules
"""

import base64
import os

from .config import (
    PRIMARY_BLUE, SECONDARY_BLUE, ACCENT_BLUE, SOFT_BLUE, ULTRA_LIGHT,
    INK, MUTED, LINE_GRAY, BORDER_GRAY, WHITE,
    STATUS_ACCENT, STATUS_BG,
    diseases_info,
    REPORT_METADATA, BENCHMARKS, REFERENCES, LIMITATIONS,
    TOC_SECTIONS,
    RISK_LABELS, AI_DECISION_COLOR_MAP, URGENCY_MAP,
    SEVERITY_LEVELS, PRIORITY_COLORS,
)
from .icons import vector_icon
from .flowables import gradient_progress_bar, risk_gauge
from .helpers import ar, metric_card, badge_element, build_qr_code, section_divider
from .charts import build_pie_chart, build_bar_chart
from .components import (
    build_metric_row, build_badge_row, build_quality_rows,
    build_confidence_rows, build_timeline, build_pipeline,
    build_signature_block, build_disclaimer, build_doctor_notes,
    build_version_history, build_limitations_and_references,
)


def _img_data_uri(image_path):
    """Best-effort: read a local image file and return a base64 data: URI.
    Returns None if the file can't be read (keeps the report resilient)."""
    try:
        if not image_path or not os.path.exists(image_path):
            return None
        ext = os.path.splitext(image_path)[1].lower().lstrip('.') or 'png'
        mime = 'jpeg' if ext in ('jpg', 'jpeg') else ext
        with open(image_path, 'rb') as f:
            b64 = base64.b64encode(f.read()).decode('ascii')
        return f"data:image/{mime};base64,{b64}"
    except Exception:
        return None


# =====================================================================================
# SECTION 0: COVER PAGE
# =====================================================================================

def build_cover_page(report_id, report_date, report_time, patient_name,
                     image_path=None, logo_path=None):
    """Build the cover page of the report."""
    logo_uri = _img_data_uri(logo_path)
    logo_html = f'<img src="{logo_uri}" style="width:2.2cm;height:2.2cm;object-fit:contain;"/>' if logo_uri else vector_icon("logo", 80, PRIMARY_BLUE)

    xray_html = ""
    xray_uri = _img_data_uri(image_path)
    if xray_uri:
        xray_html = f"""
<div style="margin:0.5cm auto 0.3cm auto;width:7.4cm;height:7.4cm;background:{INK};
            border:2pt solid {PRIMARY_BLUE};display:flex;align-items:center;justify-content:center;">
  <img src="{xray_uri}" style="max-width:7cm;max-height:7cm;"/>
</div>"""

    verify_url = f"https://respai.app/verify/{report_id}"

    return f"""
<div class="cover-page">
  <div class="spacer-lg"></div>
  {logo_html}
  <div class="spacer-md"></div>
  <div style="font-family:inherit;font-weight:bold;font-size:32pt;color:{PRIMARY_BLUE};">RespAI</div>
  <div style="font-weight:bold;font-size:17pt;color:{SECONDARY_BLUE};">AI Chest X-ray Diagnostic Report</div>
  <div class="spacer-lg"></div>
  <div style="width:12cm;height:2.5px;background:{PRIMARY_BLUE};margin:0 auto;border-radius:1px;"></div>
  <div class="spacer-lg"></div>
  <table class="plain-table" style="width:12cm;margin:0 auto;">
    <tr><td style="width:33%;text-align:right;font-size:9pt;color:{MUTED};">{ar('اسم المريض')}</td>
        <td style="text-align:left;font-size:10pt;font-weight:bold;color:{INK};direction:ltr;">{patient_name}</td></tr>
    <tr><td style="text-align:right;font-size:9pt;color:{MUTED};">Report ID</td>
        <td style="text-align:left;font-size:10pt;font-weight:bold;color:{INK};direction:ltr;">{report_id}</td></tr>
    <tr><td style="text-align:right;font-size:9pt;color:{MUTED};">{ar('التاريخ والوقت')}</td>
        <td style="text-align:left;font-size:10pt;color:{INK};direction:ltr;">{report_date} &#8226; {report_time}</td></tr>
  </table>
  {xray_html}
  <div style="margin-top:0.4cm;">{build_qr_code(verify_url, 90)}</div>
  <div class="spacer-md"></div>
  <div class="confidential">CONFIDENTIAL MEDICAL DOCUMENT</div>
</div>
"""


# =====================================================================================
# SECTION 1: TABLE OF CONTENTS
# =====================================================================================

def build_table_of_contents():
    """Build the table of contents page."""
    rows = "".join(
        f'<tr><td style="width:1.2cm;text-align:center;font-weight:bold;color:{PRIMARY_BLUE};">{num}</td>'
        f'<td style="text-align:right;">{en_t} &#8212; {ar(ar_t)}</td></tr>'
        for num, ar_t, en_t in TOC_SECTIONS
    )
    return f"""
<div style="text-align:center;font-weight:bold;font-size:22pt;color:{PRIMARY_BLUE};margin-bottom:0.4cm;">
  {ar('فهرس التقرير')} &#8212; Table of Contents
</div>
<table class="report-table" style="border:none;">
  <tbody>{rows}</tbody>
</table>
"""


# =====================================================================================
# SECTION 2: EXECUTIVE SUMMARY
# =====================================================================================

def build_executive_summary(results, flagged, top_disease, overall_color,
                            risk_accent, risk_bg, overall_confidence,
                            ai_decision_en, ai_decision_ar, severity_score,
                            clinical_priority_en, clinical_priority_ar):
    """Build section 1: Executive Summary."""
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

    ai_clr_key = AI_DECISION_COLOR_MAP.get(ai_decision_en, 'green')
    gauge_html = risk_gauge(severity_score, risk_accent, "Risk Level", size=100)

    risk_label_en = RISK_LABELS.get(overall_color, ('NORMAL', ''))[0]
    metrics_html = build_metric_row([
        (risk_label_en, "التقييم العام", risk_accent, risk_bg),
        (ar(ai_decision_ar), "قرار النموذج", STATUS_ACCENT[ai_clr_key], STATUS_BG[ai_clr_key]),
        (f"{overall_confidence}%", "ثقة النموذج", STATUS_ACCENT['green'], STATUS_BG['green']),
    ])

    pri_html = ""
    if top_disease:
        pri_html = f"""
<div style="display:flex;gap:16pt;margin-top:0.15cm;">
  <div class="arabic-body" style="flex:1;"><b>{ar('الأولوية السريرية:')}</b> {ar(clinical_priority_ar)} ({clinical_priority_en})</div>
  <div class="arabic-body" style="flex:1;"><b>{ar('أبرز نتيجة:')}</b> {ar(top_disease['ar_name'])} &#8212; {top_disease['probability']}%</div>
</div>"""

    return f"""
{section_divider(1, "الملخص التنفيذي", "summary")}
<div class="spacer-md"></div>
<div class="box">
  <div class="arabic-subheading">{ar('الانطباع العام')} &#8212; Overall Impression</div>
  <div class="english-body">{imp_en}</div>
  <div class="arabic-body-justify">{ar(imp_ar)}</div>
</div>
<div class="spacer-sm"></div>
<div style="display:flex;align-items:center;gap:10pt;">
  <div style="flex:0 0 auto;">{gauge_html}</div>
  <div style="flex:1;">{metrics_html}</div>
</div>
{pri_html}
"""


# =====================================================================================
# SECTION 3: PATIENT INFORMATION
# =====================================================================================


def build_patient_info(patient_name, patient_age, patient_gender, patient_medical_id,
                       report_date, report_time, image_path=None, doctor_name=None):
    """Build section 2: Patient Information."""
    def _row(l1, v1, l2, v2):
        return (f'<tr><td style="width:20%;text-align:right;color:{MUTED};font-size:9pt;">{ar(l1)}</td>'
                f'<td style="width:30%;text-align:left;direction:ltr;">{v1}</td>'
                f'<td style="width:20%;text-align:right;color:{MUTED};font-size:9pt;">{ar(l2)}</td>'
                f'<td style="width:30%;text-align:left;direction:ltr;">{v2}</td></tr>')

    doctor_row = ""
    if doctor_name:
        doctor_row = (
            f'<tr><td style="width:20%;text-align:right;color:{MUTED};font-size:9pt;">{ar("الطبيب المعالج")}</td>'
            f'<td colspan="3" style="text-align:left;direction:ltr;font-weight:bold;color:{PRIMARY_BLUE};">Dr. {doctor_name}</td></tr>'
        )

    table_html = f"""
<table class="plain-table">
  {_row('اسم المريض', patient_name, 'العمر', patient_age)}
  {_row('الجنس', patient_gender, 'الرقم الطبي', patient_medical_id)}
  {_row('تاريخ التحليل', f"{report_date}&nbsp;&nbsp;{report_time}", 'تاريخ الإصدار', report_date)}
  {doctor_row}
</table>"""

    img_html = ""
    xray_uri = _img_data_uri(image_path)
    if xray_uri:
        img_html = f"""
<div class="spacer-sm"></div>
<div style="text-align:center;">
  <div style="width:5.4cm;height:5.4cm;margin:0 auto;background:{INK};border:1.5pt solid {PRIMARY_BLUE};
              display:flex;align-items:center;justify-content:center;">
    <img src="{xray_uri}" style="max-width:5cm;max-height:5cm;"/>
  </div>
  <div style="font-size:7.5pt;color:{MUTED};margin-top:5pt;">
    PA View &#8226; {REPORT_METADATA['input_resolution']} &#8226; {REPORT_METADATA['image_format']} &#8226; Preprocessed
  </div>
</div>"""

    return f"""
{section_divider(2, "بيانات المريض", "patient")}
<div class="spacer-md"></div>
{table_html}
{img_html}
"""



# =====================================================================================
# SECTION 4: DASHBOARD STATISTICS
# =====================================================================================

def build_dashboard_stats(total, flagged_count, max_prob, avg_prob, severity_score,
                          overall_confidence, processing_time, report_gen_time):
    """Build section 3: Dashboard Statistics."""
    dash1 = build_metric_row([
        (total, "Total Diseases", PRIMARY_BLUE, ULTRA_LIGHT),
        (flagged_count, "Flagged Findings", STATUS_ACCENT['orange'], STATUS_BG['orange']),
        (f"{max_prob}%", "Highest Prob.", ACCENT_BLUE, ULTRA_LIGHT),
        (f"{avg_prob}%", "Average Prob.", SECONDARY_BLUE, ULTRA_LIGHT),
    ])
    dash2 = build_metric_row([
        (f"{severity_score}", "Severity Score", STATUS_ACCENT['orange'], ULTRA_LIGHT),
        (f"{overall_confidence}%", "AI Confidence", STATUS_ACCENT['green'], STATUS_BG['green']),
        (f"{processing_time}s", "Inference Time", MUTED, ULTRA_LIGHT),
        (f"{report_gen_time}s", "Report Gen Time", MUTED, ULTRA_LIGHT),
    ])

    bench_rows = "".join(
        f'<tr><td style="direction:ltr;text-align:left;">{k}</td>'
        f'<td style="direction:ltr;text-align:left;font-weight:bold;">{v}</td></tr>'
        for k, v in BENCHMARKS.items()
    )

    return f"""
{section_divider(3, "لوحة المعلومات", "stats")}
<div class="spacer-md"></div>
{dash1}
<div class="spacer-sm"></div>
{dash2}
<div class="spacer-md"></div>
<table class="report-table">
  <thead><tr><th>Metric</th><th>Value</th></tr></thead>
  <tbody>{bench_rows}</tbody>
</table>
"""


# =====================================================================================
# SECTION 5: DETAILED FINDINGS
# =====================================================================================


# Labels/colors for the clinical "relation" tag added by result_filter.py.
# Falls back to 'associated' styling if a result has no 'relation' key
# (keeps this function safe to call on older/unfiltered result lists too).
_RELATION_LABELS = {
    'primary':     ('Primary',     PRIMARY_BLUE),
    'associated':  ('Associated',  ACCENT_BLUE),
    'independent': ('Independent', STATUS_ACCENT.get('red', '#c0392b')),
}


def build_detailed_findings(results):
    """Build section 4: Detailed Findings Table."""
    rows = []
    for res in results:
        info = diseases_info.get(res['disease'], {})
        sev_en, _ = SEVERITY_LEVELS.get(res['color'], ('Mild', 'خفيف'))
        sev_color = STATUS_ACCENT.get(res['color'], MUTED)
        rec_pri = URGENCY_MAP.get(res['color'], 'Routine')
        pr_color = PRIORITY_COLORS.get(rec_pri, MUTED)
        rel_label, rel_color = _RELATION_LABELS.get(res.get('relation', 'associated'), _RELATION_LABELS['associated'])
        rows.append(f"""
<tr>
  <td style="color:{rel_color};font-weight:bold;font-size:7.5pt;">{rel_label}</td>
  <td style="text-align:right;">{ar(res['ar_name'])}</td>
  <td style="direction:ltr;color:{MUTED};font-size:8pt;">{res['disease']}</td>
  <td>{info.get('icd10', '—')}</td>
  <td>{res['probability']}%</td>
  <td style="color:{sev_color};font-weight:bold;">{sev_en}</td>
  <td>{gradient_progress_bar(res['probability'], res['color'], width='90%', height='8px')}</td>
  <td style="color:{pr_color};font-weight:bold;font-size:7.5pt;">{rec_pri}</td>
</tr>""")

    note_html = ""
    if any(res.get('relation') == 'independent' for res in results):
        note_html = f"""
<div class="spacer-sm"></div>
<div class="arabic-body-justify" style="color:{STATUS_ACCENT.get('red', '#c0392b')};">
  {ar('ملاحظة: النتائج المصنفة "Independent" هي أمراض مستقلة عن التشخيص الأساسي ولا ترتبط به إكلينيكياً، وقد تتطلب تقييماً منفصلاً.')}
</div>"""

    return f"""
{section_divider(4, "النتائج التفصيلية", "findings")}
<div class="spacer-md"></div>
<table class="report-table">
  <thead>
    <tr>
      <th>Relation</th><th>{ar('المرض')}</th><th>Disease</th><th>ICD-10</th><th>{ar('النسبة')}</th>
      <th>Severity</th><th>Progress</th><th>Priority</th>
    </tr>
  </thead>
  <tbody>{''.join(rows)}</tbody>
</table>
{note_html}
"""


# =====================================================================================
# SECTION 6: DISEASE ANALYSIS (Top 3)
# =====================================================================================

def build_disease_analysis(flagged):
    """Build section 5: Disease Analysis (Top 3)."""
    if not flagged:
        return ""

    blocks = []
    for res in flagged[:3]:
        info = diseases_info.get(res['disease'], {})
        sev_en, _ = SEVERITY_LEVELS.get(res['color'], ('Mild', 'خفيف'))

        badges_row = build_badge_row((sev_en, ''), info.get('icd10', ''), info.get('snomed_ct', ''))

        detail_rows = ""
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
            detail_rows += f'<div class="arabic-body-justify"><b>{label}:</b> {val}</div>'

        blocks.append(f"""
<div class="avoid-break" style="margin-bottom:0.3cm;">
  <div class="arabic-subheading"><b>{ar(res['ar_name'])}</b> &#8212; {res['disease']} &#8212; {res['probability']}%</div>
  <div class="spacer-sm"></div>
  {badges_row}
  <div class="spacer-sm"></div>
  {detail_rows}
  <div class="spacer-sm"></div>
  {gradient_progress_bar(res['probability'], res['color'], width='100%', height='11px')}
</div>""")

    return f"""
{section_divider(5, "تحليل الأمراض المكتشفة (Top 3)", "findings")}
<div class="spacer-md"></div>
{''.join(blocks)}
"""


# =====================================================================================
# SECTION 7: AI ANALYTICS & CHARTS
# =====================================================================================

def build_ai_analytics(results, counts):
    """Build section 6: AI Analytics & Charts."""
    pie = build_pie_chart(counts)
    bar = build_bar_chart(results)

    charts_html = f"""
<table class="plain-table">
  <tr>
    <td style="text-align:center;font-weight:bold;color:{PRIMARY_BLUE};">Risk Distribution</td>
    <td style="text-align:center;font-weight:bold;color:{PRIMARY_BLUE};">Disease Probability Ranking</td>
  </tr>
  <tr>
    <td style="text-align:center;">{pie}</td>
    <td style="text-align:center;">{bar}</td>
  </tr>
</table>"""

    conf_rows = build_confidence_rows(results)

    return f"""
{section_divider(6, "الرسوم البيانية والتحليلات", "chart")}
<div class="spacer-md"></div>
{charts_html}
<div class="spacer-md"></div>
<div class="arabic-subheading">{ar('توزيع مستويات الثقة')} &#8212; Confidence Distribution</div>
{conf_rows}
"""


# =====================================================================================
# SECTION 8: GRAD-CAM HEATMAP
# =====================================================================================

def build_heatmap():
    """Build section 7: Grad-CAM Heatmap (placeholder, compact)."""
    icon_html = vector_icon("heatmap", 26, MUTED)
    return f"""
{section_divider(7, "خريطة الحرارة", "heatmap")}
<div class="spacer-sm"></div>
<div class="box" style="text-align:center;padding:8pt 10pt;display:flex;align-items:center;gap:10pt;justify-content:center;">
  <div style="flex:0 0 auto;">{icon_html}</div>
  <div style="flex:0 0 auto;text-align:right;">
    <div style="font-weight:bold;font-size:10pt;color:{MUTED};">Grad-CAM Heatmap Visualization &#8212; Feature Not Enabled</div>
    <div style="font-size:8pt;color:{MUTED};">
      {ar('Original Image → Grad-CAM Overlay → Attention Map — ستتوفر في الإصدارات القادمة')}
    </div>
  </div>
</div>
"""


# =====================================================================================
# SECTION 9: CLINICAL INTERPRETATION
# =====================================================================================

def build_clinical_interpretation(flagged, top_disease):
    """Build section 8: Clinical Interpretation."""
    if not flagged:
        return ""

    top_html = ""
    if top_disease:
        interp_text = (f"يُلاحظ وجود {ar(top_disease['ar_name'])} بنسبة احتمالية "
                       f"{top_disease['probability']}%، مما يستدعي تقييماً سريرياً شاملاً.")
        top_html = f'<div class="arabic-body-justify">{ar(interp_text)}</div>'

    findings_html = ""
    for res in flagged[:3]:
        ti = diseases_info.get(res['disease'], {})
        findings_html += (f'<div class="arabic-body">&#9679;&nbsp; <b>{ar(res["ar_name"])}:</b> '
                          f'{ar(ti.get("impression", res["description"]))}</div>')

    return f"""
{section_divider(8, "التفسير السريري", "doctor")}
<div class="spacer-md"></div>
<div class="arabic-subheading">{ar('الانطباع الشعاعي')} &#8212; Radiological Impression</div>
{top_html}
<div class="spacer-sm"></div>
<div class="arabic-subheading">{ar('الارتباط السريري')} &#8212; Clinical Correlation</div>
<div class="arabic-body-justify">{ar('يجب ربط النتائج بالأعراض السريرية والفحوصات المخبرية قبل اتخاذ أي قرار علاجي.')}</div>
<div class="spacer-sm"></div>
<div class="arabic-subheading">{ar('النتائج المتوقعة')} &#8212; Expected Findings</div>
{findings_html}
"""


# =====================================================================================
# SECTION 10: CLINICAL DECISION SUPPORT
# =====================================================================================

def build_clinical_decision_support(flagged):
    """Build section 9: Clinical Decision Support."""
    if not flagged:
        return ""

    rows = []
    for res in flagged[:5]:
        ti = diseases_info.get(res['disease'], {})
        rows.append(f"""
<tr>
  <td style="direction:ltr;text-align:left;">{res['disease']}</td>
  <td style="direction:ltr;text-align:left;">{ti.get('test', '—')}</td>
  <td style="direction:ltr;text-align:left;">{ti.get('medication', '—')}</td>
  <td style="direction:ltr;text-align:left;">{ti.get('specialist', '—')}</td>
  <td style="direction:ltr;text-align:left;">{ti.get('followup', '—')}</td>
</tr>""")

    return f"""
{section_divider(9, "دعم القرار السريري", "recommend")}
<div class="spacer-md"></div>
<table class="report-table">
  <thead><tr><th>Disease</th><th>Recommended Test</th><th>Medication</th><th>Specialist</th><th>Follow-up</th></tr></thead>
  <tbody>{''.join(rows)}</tbody>
</table>
"""


# =====================================================================================
# SECTION 11: AI RECOMMENDATIONS
# =====================================================================================

def build_ai_recommendations(flagged):
    """Build section 10: AI Recommendations."""
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

    rec_html = ""
    for title, items in sections_rec:
        items_html = "".join(f'<div class="arabic-body">&#9679;&nbsp; {ar(it)}</div>' for it in items)
        rec_html += f'<div class="arabic-subheading">{ar(title)}</div>{items_html}<div class="spacer-sm"></div>'

    special_html = ""
    if flagged:
        special_items = "".join(
            f'<div class="arabic-body">&#9679;&nbsp; <b>{ar(res["ar_name"])}:</b> '
            f'{diseases_info.get(res["disease"], {}).get("recommendation", "Observation")}</div>'
            for res in flagged[:3]
        )
        special_html = f'<div class="arabic-subheading">{ar("توصيات خاصة حسب الأمراض المكتشفة")}</div>{special_items}'

    return f"""
{section_divider(10, "توصيات الذكاء الاصطناعي", "recommend")}
<div class="spacer-md"></div>
{rec_html}
{special_html}
"""


# =====================================================================================
# SECTION 12: CONFIDENCE ANALYSIS
# =====================================================================================

def build_confidence_analysis(overall_confidence, highest_confidence, validation_auc, confidence_en, confidence_ar):
    """Build section 11: Confidence Analysis."""
    metrics_html = build_metric_row([
        (f"{overall_confidence}%", f"Overall ({confidence_ar})", ACCENT_BLUE, ULTRA_LIGHT),
        (f"{highest_confidence}%", "Highest Prediction", PRIMARY_BLUE, ULTRA_LIGHT),
        (validation_auc, "Validation AUC", STATUS_ACCENT['green'], STATUS_BG['green']),
    ])
    conf_bar_key = 'green' if overall_confidence >= 70 else 'yellow'

    return f"""
{section_divider(11, "تحليل ثقة النموذج", "confidence")}
<div class="spacer-md"></div>
{metrics_html}
<div class="spacer-md"></div>
{gradient_progress_bar(overall_confidence, conf_bar_key, width='100%', height='13px')}
<div class="spacer-sm"></div>
<div class="arabic-small">{ar(f'مستوى الثقة: {confidence_ar} ({confidence_en}). يُحسب متوسط الثقة من جميع الأمراض المفحوصة.')}</div>
"""


# =====================================================================================
# SECTION 13: EXPLAINABLE AI
# =====================================================================================

def build_explainable_ai(processing_time, report_gen_time, report_time):
    """Build section 12: Explainable AI."""
    pipe_html = build_pipeline()

    steps_html = ""
    for title, desc in [
        ("Image Preprocessing", "يتم تغيير حجم الصورة إلى 224×224 بكسل وتطبيق قيم البكسل لتحسين أداء النموذج."),
        ("Feature Extraction", "يستخدم النموذج بنية DenseNet-121 لاستخراج الميزات الشعاعية من الطبقات العميقة."),
        ("Attention Mechanism", "يركز النموذج على المناطق ذات الصلة في الأشعة باستخدام آليات الانتباه العميق."),
        ("Probability Calc.", "يتم حساب احتمالية كل مرض باستخدام دالة Sigmoid على المخرجات النهائية."),
        ("Thresholding", "تُصنف النتيجة كـ Positive إذا تجاوزت الاحتمالية عتبة 0.50 المحددة مسبقاً."),
        ("Final Classification", "يتم ترتيب النتائج تنازلياً وتحديد مستوى الخطورة والأولوية السريرية."),
    ]:
        steps_html += f'<div class="arabic-body-justify"><b>{title}:</b> {ar(desc)}</div>'

    tl_html = build_timeline(report_time, processing_time, report_gen_time)

    return f"""
{section_divider(12, "كيف اتخذ النموذج قراره", "ai")}
<div class="spacer-md"></div>
{pipe_html}
<div class="spacer-md"></div>
{steps_html}
<div class="spacer-md"></div>
<div class="arabic-subheading">{ar('الجدول الزمني للمعالجة')} &#8212; Processing Timeline</div>
{tl_html}
"""


# =====================================================================================
# SECTION 14: IMAGE QUALITY ASSESSMENT
# =====================================================================================

def build_image_quality_assessment():
    """Build section 13: Image Quality Assessment."""
    rows_html = build_quality_rows()
    return f"""
{section_divider(13, "تقييم جودة الصورة", "quality")}
<div class="spacer-md"></div>
{rows_html}
<div class="spacer-sm"></div>
<div class="arabic-small">{ar('ملاحظة: هذه القيم مرجعية حالياً وسيتم حسابها تلقائياً من الصورة في الإصدارات القادمة.')}</div>
"""


# =====================================================================================
# SECTION 15: TECHNICAL INFORMATION
# =====================================================================================

def build_technical_information(processing_time):
    """Build section 14: Technical Information."""
    def _row(l1, v1, l2, v2):
        return (f'<tr><td style="width:20%;text-align:right;color:{MUTED};font-size:9pt;">{l1}</td>'
                f'<td style="width:30%;direction:ltr;text-align:left;">{v1}</td>'
                f'<td style="width:20%;text-align:right;color:{MUTED};font-size:9pt;">{l2}</td>'
                f'<td style="width:30%;direction:ltr;text-align:left;">{v2}</td></tr>')

    table_html = f"""
<table class="plain-table">
  {_row('Model Architecture', 'DenseNet-121', 'Training Dataset', REPORT_METADATA['dataset'])}
  {_row('Training Images', REPORT_METADATA['training_images'], 'Validation AUC', REPORT_METADATA['validation_auc'])}
  {_row('Framework', REPORT_METADATA['framework'], 'Hardware', REPORT_METADATA['hardware'])}
  {_row('PyTorch Version', REPORT_METADATA['pytorch_version'], 'CUDA Version', REPORT_METADATA['cuda_version'])}
  {_row('Input Resolution', REPORT_METADATA['input_resolution'], 'Image Format', REPORT_METADATA['image_format'])}
  {_row('Prediction Threshold', REPORT_METADATA['threshold'], 'Inference Time', f"{processing_time} s")}
  {_row('Report Version', f"v{REPORT_METADATA['report_version']}", 'Model Version', REPORT_METADATA['model_version'])}
</table>"""

    ver_html = build_version_history()

    return f"""
{section_divider(14, "المعلومات التقنية", "tech")}
<div class="spacer-md"></div>
{table_html}
<div class="spacer-md"></div>
<div class="arabic-subheading">{ar('سجل إصدارات النموذج')} &#8212; AI Version History</div>
{ver_html}
"""


# =====================================================================================
# SECTION 16: LIMITATIONS & REFERENCES + DISCLAIMER + DOCTOR NOTES
# =====================================================================================

def build_limitations_references_disclaimer_notes():
    """Build section 15: Limitations, References, Disclaimer."""
    return f"""
{section_divider(15, "حدود النظام والمراجع", "book")}
<div class="spacer-md"></div>
{build_limitations_and_references()}
<div class="spacer-md"></div>
{build_disclaimer()}
"""


# =====================================================================================
# SECTION 17: VERIFICATION & SIGNATURES
# =====================================================================================

def build_verification_signatures(report_id, report_date, report_time, verification_hash):
    """Build section 16: Verification & Signatures (includes Doctor's Notes)."""
    verify_url = f"https://respai.app/verify/{report_id}"
    sig_html = build_signature_block(report_id, report_date, report_time, verify_url, verification_hash)
    notes_html = build_doctor_notes(6)
    return f"""
{section_divider(16, "التوقيعات والتحقق", "shield")}
<div class="spacer-md"></div>
{notes_html}
<div class="spacer-md"></div>
{sig_html}
"""


# =====================================================================================
# SECTION 18: FINAL PAGE
# =====================================================================================

def build_final_page(flagged, top_disease, max_prob, overall_confidence, confidence_ar,
                     clinical_priority_en, ai_decision_en, ai_decision_ar, priority_color,
                     patient_status, patient_status_color, report_date):
    """Build the final page with clinical impression and summary."""
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

    fci_block = f"""
<div class="box" style="border:1.2pt solid {PRIMARY_BLUE};text-align:center;padding:10pt 12pt;">
  <div style="font-weight:bold;font-size:16pt;color:{PRIMARY_BLUE};">FINAL CLINICAL IMPRESSION</div>
  <div class="spacer-sm"></div>
  <div class="english-body" style="text-align:center;">{fci_en}</div>
  <div class="arabic-body-justify">{ar(fci_ar)}</div>
</div>"""

    def _row(l1, v1, l2, v2, v1_color=INK, v2_color=INK):
        return (f'<tr><td style="width:20%;text-align:right;color:{MUTED};font-size:9pt;">{l1}</td>'
                f'<td style="width:30%;direction:ltr;text-align:left;color:{v1_color};font-weight:bold;">{v1}</td>'
                f'<td style="width:20%;text-align:right;color:{MUTED};font-size:9pt;">{l2}</td>'
                f'<td style="width:30%;direction:ltr;text-align:left;color:{v2_color};">{v2}</td></tr>')

    summary_html = f"""
<div style="font-weight:bold;font-size:14pt;color:{PRIMARY_BLUE};text-align:right;">{ar('ملخص التقرير النهائي')} &#8212; Final Report Summary</div>
<div class="spacer-sm"></div>
<table class="plain-table">
  {_row('Patient Status', patient_status, 'Most Likely Disease', top_disease['disease'] if top_disease else '—', v1_color=patient_status_color)}
  {_row('Highest Probability', f"{max_prob}%", 'AI Confidence', f"{overall_confidence}% ({confidence_ar})")}
  {_row('Final Recommendation', clinical_priority_en, 'AI Decision', f"{ai_decision_en} ({ar(ai_decision_ar)})", v1_color=priority_color)}
</table>"""

    sys_html = f"""
<div class="spacer-lg"></div>
<div style="font-weight:bold;font-size:14pt;color:{PRIMARY_BLUE};text-align:right;">{ar('معلومات النظام')} &#8212; System Information</div>
<div class="spacer-sm"></div>
<table class="plain-table">
  <tr><td style="width:25%;text-align:right;color:{MUTED};font-size:9pt;">System Name</td>
      <td style="direction:ltr;text-align:left;">RespAI &#8212; Medical AI Diagnostic System</td></tr>
  <tr><td style="text-align:right;color:{MUTED};font-size:9pt;">Version</td>
      <td style="direction:ltr;text-align:left;">Report v{REPORT_METADATA['report_version']} &#8226; Model {REPORT_METADATA['model_version']}</td></tr>
  <tr><td style="text-align:right;color:{MUTED};font-size:9pt;">Model</td>
      <td style="direction:ltr;text-align:left;">{REPORT_METADATA['model_name']} (DenseNet-121)</td></tr>
  <tr><td style="text-align:right;color:{MUTED};font-size:9pt;">Dataset</td>
      <td style="direction:ltr;text-align:left;">{REPORT_METADATA['dataset']} &#8212; {REPORT_METADATA['training_images']} images</td></tr>
  <tr><td style="text-align:right;color:{MUTED};font-size:9pt;">Intended Use</td>
      <td style="direction:ltr;text-align:left;">Clinical Decision Support / Research</td></tr>
</table>"""

    privacy_items = "".join(
        f'<div class="arabic-body-justify">&#9679;&nbsp; {ar(p)}</div>'
        for p in [
            "يتم التعامل مع جميع بيانات المريض بسرية تامة وفقاً لأنظمة HIPAA / GDPR.",
            "لا يتم تخزين الصور أو البيانات الشخصية على خوادم خارجية دون موافقة خطية.",
            "هذا التقرير أداة مساعدة للقرار السريري وليس بديلاً عن الحكم الطبي المتخصص.",
            "يمكن التحقق من صحة التقرير عبر رمز QR أو بصمة التحقق الرقمية المرفقة.",
            "أي تعديل على محتوى التقرير يُفقده صفته الرسمية ويُعد باطلاً.",
        ]
    )

    footer_html = f"""
<div class="spacer-lg"></div>
<div style="font-weight:bold;font-size:14pt;color:{PRIMARY_BLUE};text-align:right;">{ar('سياسة الخصوصية والاستخدام')}</div>
<div class="spacer-sm"></div>
{privacy_items}
<div class="spacer-md"></div>
<div class="arabic-body-justify">{ar(f'جميع حقوق هذا التقرير محفوظة © {report_date[:4]} RespAI. يُمنع نسخ أو تعديل أو إعادة توزيع هذا التقرير دون إذن خطي مسبق.')}</div>
<div class="spacer-sm"></div>
<div class="english-body">support@respai.app &#8226; www.respai.app &#8226; +000 000 000 000</div>"""

    about_respai = f"""
<div class="spacer-lg"></div>
<div style="border-top:2px solid {PRIMARY_BLUE};padding-top:16pt;"></div>
<div style="font-weight:bold;font-size:16pt;color:{PRIMARY_BLUE};text-align:center;">About RespAI</div>
<div class="spacer-sm"></div>
<div style="text-align:center;font-size:10pt;color:{MUTED};">AI-powered Chest X-ray Analysis & Clinical Decision Support System</div>
<div class="spacer-md"></div>
<table class="plain-table" style="width:100%;">
<tr><td style="width:30%;color:{MUTED};font-weight:bold;">Developer</td><td style="direction:ltr;">Youseff Abdalrahman Eladl</td></tr>
<tr><td style="color:{MUTED};font-weight:bold;">Organization</td><td style="direction:ltr;">RespAI Team</td></tr>
<tr><td style="color:{MUTED};font-weight:bold;">Email</td><td style="direction:ltr;">respai.team@gmail.com</td></tr>
<tr><td style="color:{MUTED};font-weight:bold;">Version</td><td style="direction:ltr;">RespAI v1.0</td></tr>
</table>
<div class="spacer-md"></div>
<div style="text-align:center;font-size:8.5pt;color:{MUTED};">© 2026 RespAI Team. All Rights Reserved.</div>
"""

    return (
        fci_block
        + "<div class='spacer-lg'></div>"
        + summary_html
        + sys_html
        + footer_html
        + about_respai
    )