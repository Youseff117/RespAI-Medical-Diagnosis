"""
RespAI PDF Report Generator Package
====================================
"""

# استورد الدوال الأساسية من الملفات المختلفة
from .pdf_report import generate_pdf_report
from .computations import analyze_results, get_top_findings

__version__ = "5.0.0"
__author__ = "RespAI Team"

# عرّف الـ public API
__all__ = [
    'generate_pdf_report',
    'analyze_results',
    'get_top_findings',
]