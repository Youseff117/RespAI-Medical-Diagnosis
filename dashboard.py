"""
RespAI Dashboard - Backward Compatibility Wrapper
==================================================

This module provides backward compatibility with app.py.
All functions are imported from the pdf package.

Usage in app.py:
    import dashboard
    results = dashboard.analyze_results(probabilities)
    pdf_buffer = dashboard.generate_pdf_report(results)
"""

from pdf import generate_pdf_report, analyze_results, get_top_findings

__all__ = ['generate_pdf_report', 'analyze_results', 'get_top_findings']