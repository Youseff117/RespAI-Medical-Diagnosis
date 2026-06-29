"""
Computation Functions for PDF Report
=====================================

This module contains all computation and analysis functions:
- analyze_results(): Main analysis function (REQUIRED by app.py)
- get_top_findings(): Get flagged findings (REQUIRED by app.py)
- Helper computation functions for metrics

Dependencies:
- config.py (for thresholds, diseases_info, constants)
"""

from .config import (
    DISEASE_THRESHOLDS,
    diseases_info,
    SEVERITY_LEVELS,
    PRIORITY_COLORS,
    RISK_LABELS,
    AI_DECISION_COLOR_MAP,
    URGENCY_MAP,
)


# ═══════════════════════════════════════════════════════════════════════════
# CORE ANALYSIS FUNCTIONS (Required by app.py)
# ═══════════════════════════════════════════════════════════════════════════

def analyze_results(probabilities: dict) -> list:
    """
    Analyze disease probabilities and return structured results.
    
    This function is called by app.py and MUST maintain this signature.
    
    Args:
        probabilities: Dict mapping disease names to probability values (0.0-1.0)
    
    Returns:
        list: Sorted list of result dicts, each containing:
            - disease: str (English name)
            - ar_name: str (Arabic name)
            - probability: float (0-100)
            - color: str ('green', 'yellow', 'orange', 'red')
            - status: str (Arabic status text)
            - description: str (Arabic description)
            - flagged: bool (True if probability >= threshold)
    """
    results = []
    
    for disease, prob in probabilities.items():
        if disease not in diseases_info:
            continue
        
        threshold = DISEASE_THRESHOLDS.get(disease, 0.50)
        
        # Determine color and status based on threshold
        if prob >= threshold:
            color = "red"
            status = "محتمل ⚠️"
        elif prob >= threshold * 0.6:
            color = "orange"
            status = "يستدعي المتابعة 🔍"
        elif prob >= threshold * 0.3:
            color = "yellow"
            status = "منخفض 🟡"
        else:
            color = "green"
            status = "طبيعي ✅"
        
        results.append({
            "disease": disease,
            "ar_name": diseases_info[disease]["ar_name"],
            "probability": round(prob * 100, 1),
            "color": color,
            "status": status,
            "description": diseases_info[disease]["description"],
            "flagged": prob >= threshold,
        })
    
    # Sort by probability (descending)
    results.sort(key=lambda x: x["probability"], reverse=True)
    
    return results


def get_top_findings(results: list) -> list:
    """
    Get only the flagged (abnormal) findings from results.
    
    This function is called by app.py and MUST maintain this signature.
    
    Args:
        results: List of result dicts from analyze_results()
    
    Returns:
        list: Filtered list containing only flagged results
    """
    return [r for r in results if r["flagged"]]


# ══════════════════════════════════════════════════════════════════════════
# METRIC COMPUTATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def compute_overall_confidence(results: list) -> float:
    """
    Compute overall AI confidence as average of all probabilities.
    
    Args:
        results: List of result dicts
    
    Returns:
        float: Overall confidence percentage (0-95)
    """
    if not results:
        return 0.0
    
    avg = sum(r['probability'] for r in results) / len(results)
    return round(min(95.0, avg), 1)


def compute_severity_score(max_prob: float, flagged_count: int, total: int) -> float:
    """
    Compute severity score based on max probability and flagged ratio.
    
    Formula: (max_prob * 0.6) + (flagged_ratio * 0.4)
    
    Args:
        max_prob: Highest probability among all diseases
        flagged_count: Number of flagged (abnormal) diseases
        total: Total number of diseases analyzed
    
    Returns:
        float: Severity score (0-100)
    """
    if total == 0:
        return 0
    
    ratio = (flagged_count / total) * 100
    score = (max_prob * 0.6) + (ratio * 0.4)
    return round(min(100, max(0, score)), 1)


def get_clinical_priority(max_prob: float, color: str) -> tuple:
    """
    Get clinical priority level based on max probability and color.
    
    Args:
        max_prob: Highest probability
        color: Color code of the highest disease
    
    Returns:
        tuple: (English priority, Arabic priority)
    """
    if color == 'red' and max_prob >= 80:
        return 'Immediate', 'فوري'
    elif color == 'red' or (color == 'orange' and max_prob >= 60):
        return 'Urgent', 'عاجل'
    elif color in ('orange', 'yellow'):
        return 'Follow-up', 'متابعة'
    return 'Routine', 'روتيني'


def get_ai_decision(max_prob: float, flagged_count: int) -> tuple:
    """
    Get AI decision classification.
    
    Args:
        max_prob: Highest probability
        flagged_count: Number of flagged diseases
    
    Returns:
        tuple: (English decision, Arabic decision)
    """
    if flagged_count == 0:
        return 'Normal', 'طبيعي'
    elif max_prob < 40:
        return 'Borderline', 'حدّي'
    elif max_prob < 70:
        return 'Abnormal', 'غير طبيعي'
    return 'Critical', 'حرج'


def get_confidence_level(confidence: float) -> tuple:
    """
    Get confidence level classification.
    
    Args:
        confidence: Overall confidence percentage
    
    Returns:
        tuple: (English level, Arabic level)
    """
    if confidence >= 85:
        return 'Excellent', 'ممتاز'
    elif confidence >= 70:
        return 'Good', 'جيد'
    elif confidence >= 50:
        return 'Fair', 'متوسط'
    return 'Low', 'منخفض'


def get_quality_rating(score: int) -> str:
    """
    Get quality rating classification.
    
    Args:
        score: Quality score (0-100)
    
    Returns:
        str: Rating label ('Excellent', 'Good', 'Acceptable', 'Needs Review')
    """
    if score >= 90:
        return 'Excellent'
    elif score >= 75:
        return 'Good'
    elif score >= 60:
        return 'Acceptable'
    return 'Needs Review'


def get_risk_info(overall_color: str) -> tuple:
    """
    Get risk label information.
    
    Args:
        overall_color: Color code of the overall risk
    
    Returns:
        tuple: (English risk label, Arabic risk label)
    """
    return RISK_LABELS.get(overall_color, ("NORMAL", "طبيعي"))


def get_urgency_label(color: str) -> str:
    """
    Get urgency label for a disease.
    
    Args:
        color: Color code of the disease
    
    Returns:
        str: Urgency label ('Routine', 'Follow-up', 'Urgent', 'Immediate')
    """
    return URGENCY_MAP.get(color, 'Routine')