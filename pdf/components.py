"""
Reusable Components for PDF Report (HTML version)
====================================================

This module contains reusable UI components that are used across multiple
sections, now returning HTML strings instead of ReportLab flowables:
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
- config.py, styles.py, icons.py, flowables.py, helpers.py, computations.py
"""

from .config import (
    PRIMARY_BLUE, SECONDARY_BLUE, ACCENT_BLUE, SOFT_BLUE, ULTRA_LIGHT,
    INK, MUTED, LINE_GRAY, BORDER_GRAY, WHITE,
    STATUS_ACCENT, STATUS_BG,
    IMAGE_QUALITY_DEFAULTS,
    LIMITATIONS,
    REFERENCES,
    REPORT_METADATA,
)
from .icons import vector_icon
from .flowables import gradient_progress_bar
from .helpers import ar, metric_card, badge_element, build_qr_code
from .computations import get_quality_rating


# ═══════════════════════════════════════════════════════════════════════════
# METRIC ROW BUILDER
# ══════════════════════════════════════════════════════════════════════════

def build_metric_row(cards_data):
    """
    Build a row of metric cards.

    Args:
        cards_data: List of tuples (value, label, accent_color, bg_color)

    Returns:
        str: HTML snippet.
    """
    cards = "".join(metric_card(v, l, a, b) for v, l, a, b in cards_data)
    return f'<div class="metric-cards">{cards}</div>'


# ══════════════════════════════════════════════════════════════════════════
# BADGE ROW BUILDER
# ═══════════════════════════════════════════════════════════════════════════

def build_badge_row(severity, icd10, snomed):
    """
    Build a row of badges (severity, ICD-10, SNOMED).

    Args:
        severity: Tuple (English, Arabic) or plain string
        icd10: ICD-10 code string
        snomed: SNOMED CT code string

    Returns:
        str: HTML snippet.
    """
    sev_en = severity[0] if isinstance(severity, tuple) else severity
    sev_key = {'Mild': 'green', 'Moderate': 'yellow', 'Significant': 'orange', 'Severe': 'red'}.get(sev_en, 'green')
    sev_color = STATUS_ACCENT.get(sev_key, MUTED)

    sev_badge = badge_element(sev_en, sev_color)
    icd_badge = badge_element(icd10 or '—', SECONDARY_BLUE)
    return (
        f'<div style="display:flex;align-items:center;gap:8pt;direction:ltr;justify-content:flex-end;">'
        f'{sev_badge}{icd_badge}'
        f'<span style="font-size:8pt;color:{MUTED};">SNOMED: {snomed or "—"}</span>'
        f'</div>'
    )


# ══════════════════════════════════════════════════════════════════════════
# QUALITY ROW BUILDER
# ═══════════════════════════════════════════════════════════════════════════

def build_quality_rows():
    """
    Build all quality assessment rows.

    Returns:
        str: HTML snippet (concatenated rows).
    """
    rating_color = {
        'Excellent': STATUS_ACCENT['green'],
        'Good': ACCENT_BLUE,
        'Acceptable': STATUS_ACCENT['yellow'],
        'Needs Review': STATUS_ACCENT['red'],
    }
    rows = []
    for label, score in IMAGE_QUALITY_DEFAULTS:
        rating = get_quality_rating(score)
        rat_clr = rating_color[rating]
        bar_key = 'green' if score >= 85 else 'yellow' if score >= 70 else 'orange'
        rows.append(f"""
<div style="display:flex;align-items:center;gap:8pt;padding:3pt 0;">
  <div style="flex:0 0 90pt;font-family:inherit;font-size:9pt;color:{INK};direction:ltr;text-align:left;">{label}</div>
  <div style="flex:1;">{gradient_progress_bar(score, bar_key, width='100%', height='9px')}</div>
  <div style="flex:0 0 30pt;text-align:center;font-size:9pt;font-weight:bold;color:{PRIMARY_BLUE};">{score}%</div>
  <div style="flex:0 0 60pt;text-align:center;font-size:8pt;font-weight:bold;color:{rat_clr};">{rating}</div>
</div>""")
    return "".join(rows)


# ═══════════════════════════════════════════════════════════════════════════
# CONFIDENCE ROW BUILDER
# ═══════════════════════════════════════════════════════════════════════════

def build_confidence_rows(results):
    """
    Build confidence distribution rows.

    Returns:
        str: HTML snippet.
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
        rows.append(f"""
<div style="display:flex;align-items:center;gap:8pt;padding:3pt 0;">
  <div style="flex:0 0 110pt;font-size:9pt;color:{INK};direction:ltr;text-align:left;">{label}</div>
  <div style="flex:1;">{gradient_progress_bar(pct, clr_key, width='100%', height='9px')}</div>
  <div style="flex:0 0 30pt;text-align:center;font-size:9pt;font-weight:bold;color:{STATUS_ACCENT[clr_key]};">{count}</div>
</div>""")
    return "".join(rows)


# ═══════════════════════════════════════════════════════════════════════════
# TIMELINE BUILDER
# ═══════════════════════════════════════════════════════════════════════════

def build_timeline(report_time, processing_time, report_gen_time):
    """
    Build the processing timeline.

    Returns:
        str: HTML snippet.
    """
    tl_steps = [
        ("Image Uploaded", report_time),
        ("Preprocessing", f"+{round(processing_time * 0.1, 2)}s"),
        ("AI Analysis", f"+{round(processing_time * 0.6, 2)}s"),
        ("Classification", f"+{round(processing_time * 0.8, 2)}s"),
        ("Report Generated", f"+{report_gen_time}s"),
    ]
    steps_html = "".join(
        f'<div class="timeline-step"><div class="step-name">{step}</div>'
        f'<div class="step-time">{ts}</div></div>'
        for step, ts in tl_steps
    )
    return f'<div class="timeline-row" style="direction:ltr;">{steps_html}</div>'


# ═══════════════════════════════════════════════════════════════════════════
# PIPELINE BUILDER
# ═══════════════════════════════════════════════════════════════════════════

def build_pipeline():
    """
    Build the AI pipeline diagram.

    Returns:
        str: HTML snippet.
    """
    dark_colors = {ACCENT_BLUE, SECONDARY_BLUE, PRIMARY_BLUE}
    pipe_steps = [
        ("Input<br/>X-ray", SOFT_BLUE),
        ("Resize<br/>224x224", SOFT_BLUE),
        ("Normalize<br/>Pixels", SOFT_BLUE),
        ("DenseNet-121<br/>Feats", ACCENT_BLUE),
        ("Sigmoid<br/>Activation", SECONDARY_BLUE),
        ("Threshold<br/>0.50", PRIMARY_BLUE),
        ("Output<br/>Preds", STATUS_BG['green']),
    ]
    steps_html = []
    for label, bg in pipe_steps:
        txt_color = WHITE if bg in dark_colors else INK
        steps_html.append(
            f'<div class="pipeline-step" style="background:{bg};color:{txt_color};">{label}</div>'
        )
    return f'<div class="pipeline-row" style="direction:ltr;">{"".join(steps_html)}</div>'


# ═══════════════════════════════════════════════════════════════════════════
# SIGNATURE BLOCK BUILDER
# ══════════════════════════════════════════════════════════════════════════

def build_signature_block(report_id, report_date, report_time, verify_url, verification_hash):
    """
    Build the complete signature and verification block.

    Returns:
        str: HTML snippet.
    """
    hospital_icon = vector_icon("hospital", 28, MUTED)
    qr_html = build_qr_code(verify_url, 80)

    sig_tbl = f"""
<table class="plain-table" style="table-layout:fixed;">
  <tr>
    <td style="text-align:center;">
      <div style="font-size:8pt;color:{MUTED};">{ar('توقيع الطبيب')}</div>
      <div style="height:1cm;"></div>
      <div style="font-size:9pt;color:{MUTED};">____________________</div>
      <div style="font-size:8pt;color:{MUTED};">Doctor Signature</div>
    </td>
    <td style="text-align:center;">
      <div style="font-size:8pt;color:{MUTED};">{ar('ختم المستشفى')}</div>
      <div style="margin:6pt 0;">{hospital_icon}</div>
      <div style="font-size:8pt;color:{MUTED};">Hospital Stamp</div>
    </td>
    <td style="text-align:center;">
      <div style="font-size:8pt;color:{MUTED};">{ar('تاريخ المراجعة')}</div>
      <div style="height:0.6cm;"></div>
      <div style="font-size:10pt;color:{INK};">{report_date}</div>
      <div style="font-size:9pt;color:{MUTED};">{report_time}</div>
      <div style="font-size:8pt;color:{MUTED};">Review Date</div>
    </td>
    <td style="text-align:center;">
      <div style="font-size:8pt;color:{MUTED};">{ar('رمز التحقق')}</div>
      <div style="margin:4pt 0;">{qr_html}</div>
      <div style="font-size:8pt;color:{MUTED};">ID: {report_id}</div>
    </td>
  </tr>
</table>"""

    hash_row = f"""
<table class="plain-table" style="background:{SOFT_BLUE};border-color:{ACCENT_BLUE};margin-top:0.15cm;">
  <tr>
    <td style="width:35%;font-size:9pt;color:{MUTED};direction:ltr;text-align:left;">SHA-256 Verification Hash</td>
    <td style="font-size:8.5pt;color:{PRIMARY_BLUE};font-weight:bold;direction:ltr;text-align:left;">{verification_hash}</td>
  </tr>
</table>"""

    verify_row = f"""
<table class="plain-table" style="margin-top:0.15cm;">
  <tr>
    <td style="width:35%;font-size:9pt;color:{MUTED};direction:ltr;text-align:left;">Verification URL</td>
    <td style="font-size:8.5pt;color:{ACCENT_BLUE};direction:ltr;text-align:left;">{verify_url}</td>
  </tr>
</table>"""

    digital_sig = f"""
<table class="plain-table" style="background:{STATUS_BG['green']};border-color:{STATUS_ACCENT['green']};margin-top:0.15cm;">
  <tr>
    <td style="width:35%;font-size:9pt;color:{MUTED};direction:ltr;text-align:left;">Digital Signature</td>
    <td style="font-size:8.5pt;color:{STATUS_ACCENT['green']};direction:ltr;text-align:left;">RSA-2048 | RespAI CA | {report_date}</td>
  </tr>
</table>"""

    return sig_tbl + hash_row + verify_row + digital_sig


# ═══════════════════════════════════════════════════════════════════════════
# DISCLAIMER BUILDER
# ══════════════════════════════════════════════════════════════════════════

def build_disclaimer():
    """
    Build the medical disclaimer.

    Returns:
        str: HTML snippet.
    """
    title = ar("تنويه طبي وقانوني مهم")
    body = ar(
        "هذا التقرير مُنشأ بواسطة نظام ذكاء اصطناعي معتمد على تقنيات التعلم العميق، "
        "وهو يُقدَّم كأداة مساعدة للقرار السريري فقط، ولا يُعد بديلاً عن التشخيص الطبي "
        "المتخصص من قبل أخصائي أشعة مؤهل. يجب دائماً تفسير النتائج في سياق الحالة "
        "السريرية الكاملة للمريض. هذا النظام لم يخضع بعد لموافقة FDA أو CE للاستخدام التشخيصي المباشر."
    )
    return (
        f'<div style="text-align:center;font-weight:bold;font-size:11pt;color:#7A1F1F;margin-bottom:4pt;">{title}</div>'
        f'<div class="disclaimer">{body}</div>'
    )


# ═══════════════════════════════════════════════════════════════════════════
# DOCTOR NOTES BUILDER
# ═══════════════════════════════════════════════════════════════════════════

def build_doctor_notes(num_lines=6, boxed=True):
    """
    Build doctor notes section with a clear heading and horizontal write-in lines.

    Args:
        num_lines: number of blank lines for the doctor to write on.
        boxed: if True, wraps the lines in a bordered box so the section is
               visually distinct instead of reading as blank whitespace.

    Returns:
        str: HTML snippet.
    """
    lines = "".join('<div class="doctor-note-line"></div>' for _ in range(num_lines))
    heading = (
        f'<div class="arabic-subheading">{ar("ملاحظات الطبيب")} &#8212; '
        f'Doctor&#39;s Notes</div>'
    )
    if boxed:
        return (
            f'{heading}'
            f'<div class="box" style="padding:10pt 12pt;">{lines}</div>'
        )
    return heading + lines


# ═══════════════════════════════════════════════════════════════════════════
# VERSION HISTORY BUILDER
# ══════════════════════════════════════════════════════════════════════════

def build_version_history():
    """
    Build the AI version history table.

    Returns:
        str: HTML snippet.
    """
    rows_data = [
        ("RespAI System", f"v{REPORT_METADATA['report_version']}"),
        ("CheXNet Model", REPORT_METADATA['model_version']),
        ("DenseNet-121", "Pretrained (ImageNet)"),
        ("PyTorch", REPORT_METADATA['pytorch_version']),
        ("CUDA", REPORT_METADATA['cuda_version']),
    ]
    rows_html = "".join(
        f'<tr><td style="direction:ltr;text-align:left;">{k}</td>'
        f'<td style="direction:ltr;text-align:left;font-weight:bold;">{v}</td></tr>'
        for k, v in rows_data
    )
    return f"""
<table class="report-table">
  <thead><tr><th>Component</th><th>Version</th></tr></thead>
  <tbody>{rows_html}</tbody>
</table>"""


# ══════════════════════════════════════════════════════════════════════════
# LIMITATIONS & REFERENCES BUILDER
# ═══════════════════════════════════════════════════════════════════════════

def build_limitations_and_references():
    """
    Build limitations and references section.

    Returns:
        str: HTML snippet.
    """
    lim_items = "".join(f'<div class="arabic-body-justify">&#9679;&nbsp; {ar(item)}</div>' for item in LIMITATIONS)
    ref_items = "".join(
        f'<div class="arabic-body-justify" style="direction:ltr;text-align:left;">[{i}]&nbsp; {ref}</div>'
        for i, ref in enumerate(REFERENCES, 1)
    )
    return (
        f'<div class="arabic-subheading">{ar("حدود النظام  Limitations")}</div>'
        f'{lim_items}'
        f'<div class="spacer-md"></div>'
        f'<div class="arabic-subheading">{ar("المراجع العلمية  References (APA)")}</div>'
        f'{ref_items}'
    )