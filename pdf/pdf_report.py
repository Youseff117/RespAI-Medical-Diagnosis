"""
Main PDF Report Generator
==========================

This is the orchestrator module that assembles all sections into a complete PDF report.

Dependencies:
- All other pdf modules
"""

from io import BytesIO
import time
import uuid
import os
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, PageBreak, Spacer  # ← Spacer نُقل للأعلى

from .config import (
    diseases_info, DISEASE_THRESHOLDS,
    RISK_LABELS, AI_DECISION_COLOR_MAP,
    STATUS_ACCENT, STATUS_BG, PRIORITY_COLORS,
)
from .styles import get_custom_styles
from .helpers import header_footer, compute_verification_hash
from .computations import (
    analyze_results, get_top_findings,
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


def generate_pdf_report(results, patient_info=None, image_path=None, processing_time=None):
    """
    Generate the complete PDF report.
    
    This is the main entry point called by app.py.
    
    Args:
        results: List of result dicts from analyze_results()
        patient_info: Optional dict with patient details
        image_path: Optional path to chest X-ray image
        processing_time: Optional processing time in seconds
    
    Returns:
        BytesIO: PDF file buffer
    """
    gen_start = time.time()
    analysis_time = datetime.now()
    buffer = BytesIO()
    
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2 * cm, leftMargin=2 * cm,
        topMargin=2.6 * cm, bottomMargin=2.6 * cm,
    )
    styles = get_custom_styles()
    elements = []
    
    # ── Metadata ─────────────────────────────────────────────
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
    
    # ── Build all sections ────────────────────────────────────

    elements.extend(build_cover_page(
        report_id, report_date, report_time, patient_name,
        image_path=image_path, logo_path=logo_path if has_logo else None
    ))
    elements.append(PageBreak())
    
    elements.extend(build_table_of_contents())
    elements.append(PageBreak())
    
    elements.extend(build_executive_summary(
        results, flagged, top_disease, overall_color,
        risk_accent, risk_bg, overall_confidence,
        ai_decision_en, ai_decision_ar, severity_score,
        clinical_priority_en, clinical_priority_ar,
    ))
    elements.append(Spacer(1, 0.4 * cm))
    
    elements.extend(build_patient_info(
        patient_name, patient_age, patient_gender, patient_medical_id,
        report_date, report_time, image_path=image_path,
    ))
    elements.append(Spacer(1, 0.4 * cm))
    
    elements.extend(build_dashboard_stats(
        total, len(flagged), max_prob, avg_prob, severity_score,
        overall_confidence, processing_time, report_gen_time,
    ))
    elements.append(Spacer(1, 0.4 * cm))
    
    elements.extend(build_detailed_findings(results))
    elements.append(Spacer(1, 0.4 * cm))
    
    elements.extend(build_disease_analysis(flagged))
    elements.append(Spacer(1, 0.4 * cm))
    
    elements.extend(build_ai_analytics(results, counts))
    elements.append(Spacer(1, 0.4 * cm))
    
    elements.extend(build_heatmap())
    elements.append(Spacer(1, 0.4 * cm))
    
    elements.extend(build_clinical_interpretation(flagged, top_disease))
    elements.append(Spacer(1, 0.4 * cm))
    
    elements.extend(build_clinical_decision_support(flagged))
    elements.append(Spacer(1, 0.4 * cm))
    
    elements.extend(build_ai_recommendations(flagged))
    elements.append(Spacer(1, 0.4 * cm))
    
    elements.extend(build_confidence_analysis(
        overall_confidence, highest_confidence, validation_auc,
        confidence_en, confidence_ar,
    ))
    elements.append(Spacer(1, 0.4 * cm))
    
    elements.extend(build_explainable_ai(
        processing_time, report_gen_time, report_time,
    ))
    elements.append(PageBreak())
    
    elements.extend(build_image_quality_assessment())
    elements.append(Spacer(1, 0.4 * cm))
    
    elements.extend(build_technical_information(processing_time))
    elements.append(Spacer(1, 0.4 * cm))
    
    elements.extend(build_limitations_references_disclaimer_notes())
    elements.append(Spacer(1, 0.4 * cm))
    
    elements.extend(build_verification_signatures(
        report_id, report_date, report_time, verification_hash,
    ))
    elements.append(PageBreak())
    
    patient_status = "Normal" if not flagged else "Abnormal"
    patient_status_color = STATUS_ACCENT['green'] if not flagged else STATUS_ACCENT['orange']
    
    elements.extend(build_final_page(
        flagged, top_disease, max_prob, overall_confidence, confidence_ar,
        clinical_priority_en, ai_decision_en, ai_decision_ar, priority_color,
        patient_status, patient_status_color, report_date,
    ))
    
    # ── Build PDF ─────────────────────────────────────────────
    def _hf(canvas, doc):
        header_footer(canvas, doc, logo_path=logo_path if has_logo else None)
    
    doc.build(elements, onFirstPage=_hf, onLaterPages=_hf)
    buffer.seek(0)
    return buffer