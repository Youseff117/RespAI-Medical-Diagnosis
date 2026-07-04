"""
Main PDF Report Generator (WeasyPrint version)

This is the orchestrator module that assembles all sections into a complete
HTML document and renders it to PDF using WeasyPrint (instead of ReportLab's
SimpleDocTemplate). WeasyPrint renders through Pango/HarfBuzz, giving correct
Arabic shaping + RTL layout natively.

Public entry point (same signature as before, called by dashboard.py -> app.py):
generate_pdf_report(results, patient_info=None, doctor_name=None, image_path=None, processing_time=None)
"""

from io import BytesIO
import time
import uuid
import os
from datetime import datetime

from weasyprint import HTML

from .config import (
    RISK_LABELS, STATUS_ACCENT, STATUS_BG, PRIORITY_COLORS,
)
from .styles import get_css
from .helpers import compute_verification_hash, page_header_bar_html
from .computations import (
    compute_overall_confidence, compute_severity_score,
    get_clinical_priority, get_ai_decision, get_confidence_level,
)
from .sections import (
    build_cover_page, build_table_of_contents,
    build_executive_summary, build_patient_info,
    build_dashboard_stats, build_detailed_findings,
    build_disease_analysis, build_ai_analytics,
    build_heatmap, build_clinical_interpretation,
    build_clinical_decision_support, build_ai_recommendations,
    build_confidence_analysis, build_explainable_ai,
    build_image_quality_assessment, build_technical_information,
    build_limitations_references_disclaimer_notes,
    build_verification_signatures, build_final_page,
)

# Project root, used as base_url so relative paths like "static/uploads/x.jpg"
# and "static/fonts/Cairo-Regular.ttf" resolve the same way they did for
# ReportLab (which resolved them relative to the process's working directory).
_PROJECT_ROOT = os.getcwd()


def generate_pdf_report(results, patient_info=None, doctor_name=None, image_path=None, processing_time=None):
    """
    Generate the complete PDF report.
    This is the main entry point called by app.py (via dashboard.py).

    Args:
        results: List of result dicts from analyze_results()
        patient_info: Optional dict with patient details
        doctor_name: Optional str — the referring/linked doctor's display name.
                     When provided, it's shown in the Patient Information section.
        image_path: Optional path to chest X-ray image
        processing_time: Optional processing time in seconds

    Returns:
        BytesIO: PDF file buffer
    """
    gen_start = time.time()
    analysis_time = datetime.now()

    # ── Metadata ──────────────────────────────────────────────
    report_id = str(uuid.uuid4())[:10].upper()
    report_date = analysis_time.strftime("%Y-%m-%d")
    report_time = analysis_time.strftime("%H:%M:%S")

    if not patient_info:
        patient_info = {}
    patient_name = patient_info.get("name", "—")
    patient_age = patient_info.get("age", "—")
    patient_gender = patient_info.get("gender", "—")
    patient_medical_id = patient_info.get("medical_id", f"PID-{report_id}")

    # ── Stats ─────────────────────────────────────────────────
    flagged = [r for r in results if r["flagged"]]
    total = len(results)
    counts = {c: len([r for r in results if r['color'] == c])
              for c in ('green', 'yellow', 'orange', 'red')}
    avg_prob = round(sum(r['probability'] for r in results) / max(total, 1), 2)
    max_prob = max((r['probability'] for r in results), default=0)
    top_disease = results[0] if results else None

    overall_color = top_disease['color'] if top_disease else 'green'
    risk_en, risk_ar = RISK_LABELS.get(overall_color, ("NORMAL", "طبيعي"))
    risk_accent = STATUS_ACCENT[overall_color]
    risk_bg = STATUS_BG[overall_color]

    overall_confidence = compute_overall_confidence(results)
    highest_confidence = round(max_prob, 1)
    confidence_en, confidence_ar = get_confidence_level(overall_confidence)
    severity_score = compute_severity_score(max_prob, len(flagged), total)
    ai_decision_en, ai_decision_ar = get_ai_decision(max_prob, len(flagged))
    clinical_priority_en, clinical_priority_ar = get_clinical_priority(max_prob, overall_color)
    priority_color = PRIORITY_COLORS.get(clinical_priority_en, STATUS_ACCENT['green'])
    verification_hash = compute_verification_hash(report_id, results, analysis_time.isoformat())

    if processing_time is None:
        processing_time = round(time.time() - gen_start, 3)
    report_gen_time = round(time.time() - gen_start, 3)

    validation_auc = "0.841"
    logo_path = os.path.join("static", "logo.png")
    has_logo = os.path.exists(logo_path)

    # ── Build all sections (each returns an HTML fragment) ──────
    parts = []

    parts.append('<div class="cover-page-wrap">')
    parts.append(build_cover_page(
        report_id, report_date, report_time, patient_name,
        image_path=image_path, logo_path=logo_path if has_logo else None
    ))
    parts.append('</div>')

    parts.append('<div class="page-break">')
    parts.append(build_table_of_contents())
    parts.append('</div>')

    parts.append('<div class="page-break">')
    parts.append(build_executive_summary(
        results, flagged, top_disease, overall_color,
        risk_accent, risk_bg, overall_confidence,
        ai_decision_en, ai_decision_ar, severity_score,
        clinical_priority_en, clinical_priority_ar,
    ))
    parts.append('<div class="spacer-md"></div>')

    parts.append(build_patient_info(
        patient_name, patient_age, patient_gender, patient_medical_id,
        report_date, report_time, image_path=image_path, doctor_name=doctor_name,
    ))
    parts.append('<div class="spacer-md"></div>')

    parts.append(build_dashboard_stats(
        total, len(flagged), max_prob, avg_prob, severity_score,
        overall_confidence, processing_time, report_gen_time,
    ))
    parts.append('<div class="spacer-md"></div>')

    parts.append(build_detailed_findings(results))
    parts.append('<div class="spacer-md"></div>')

    parts.append(build_disease_analysis(flagged))
    parts.append('<div class="spacer-md"></div>')

    parts.append(build_ai_analytics(results, counts))
    parts.append('<div class="spacer-md"></div>')

    parts.append(build_heatmap())
    parts.append('<div class="spacer-md"></div>')

    parts.append(build_clinical_interpretation(flagged, top_disease))
    parts.append('<div class="spacer-md"></div>')

    parts.append(build_clinical_decision_support(flagged))
    parts.append('<div class="spacer-md"></div>')

    parts.append(build_ai_recommendations(flagged))
    parts.append('<div class="spacer-md"></div>')

    parts.append(build_confidence_analysis(
        overall_confidence, highest_confidence, validation_auc,
        confidence_en, confidence_ar,
    ))
    parts.append('<div class="spacer-md"></div>')

    parts.append(build_explainable_ai(
        processing_time, report_gen_time, report_time,
    ))
    parts.append('</div>')  # end page-break wrapper

    parts.append('<div class="page-break">')
    parts.append(build_image_quality_assessment())
    parts.append('<div class="spacer-md"></div>')

    parts.append(build_technical_information(processing_time))
    parts.append('<div class="spacer-md"></div>')

    parts.append(build_limitations_references_disclaimer_notes())
    parts.append('<div class="spacer-md"></div>')

    parts.append(build_verification_signatures(
        report_id, report_date, report_time, verification_hash,
    ))
    parts.append('</div>')

    patient_status = "Normal" if not flagged else "Abnormal"
    patient_status_color = STATUS_ACCENT['green'] if not flagged else STATUS_ACCENT['orange']

    parts.append('<div class="page-break">')
    parts.append(build_final_page(
        flagged, top_disease, max_prob, overall_confidence, confidence_ar,
        clinical_priority_en, ai_decision_en, ai_decision_ar, priority_color,
        patient_status, patient_status_color, report_date,
    ))
    parts.append('</div>')

    body_html = "\n".join(parts)

    html_doc = f"""<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
<meta charset="utf-8"/>
<style>{get_css()}</style>
</head>
<body>
{page_header_bar_html()}
{body_html}
</body>
</html>"""

    # ── Render to PDF via WeasyPrint ─────────────────────────
    buffer = BytesIO()
    HTML(string=html_doc, base_url=_PROJECT_ROOT).write_pdf(buffer)
    buffer.seek(0)
    return buffer