"""
Helper Functions for PDF Generation
====================================

This module contains utility functions used throughout the PDF report generation:
- Arabic text reshaping
- Metric cards, badges, QR codes
- Section dividers
- Header/Footer
- Verification hash computation

Dependencies:
- config.py (for colors, constants)
- styles.py (for fonts)
- icons.py (for vector icons)
- flowables.py (for custom flowables)
"""

import os
import hashlib
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, Image
from reportlab.graphics.shapes import Drawing, Rect, String

from .config import (
    PRIMARY_BLUE, SECONDARY_BLUE, ACCENT_BLUE, SOFT_BLUE, ULTRA_LIGHT,
    INK, MUTED, LINE_GRAY, BORDER_GRAY, WHITE,
    STATUS_ACCENT, STATUS_BG,
)
from .styles import (
    FONT_REGULAR, FONT_BOLD, FONT_MEDIUM, FONT_SEMIBOLD,
    CAIRO_AVAILABLE,
)
from .icons import vector_icon

# ── Optional Arabic libraries ─────────────────────────────────────────────────
try:
    import arabic_reshaper
    ARABIC_RESHAPER_AVAILABLE = True
except ImportError:
    ARABIC_RESHAPER_AVAILABLE = False

try:
    from bidi.algorithm import get_display
    BIDI_AVAILABLE = True
except ImportError:
    BIDI_AVAILABLE = False

try:
    import qrcode as _qrcode_module
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False


# ══════════════════════════════════════════════════════════════════════════
# ARABIC TEXT HELPER
# ═══════════════════════════════════════════════════════════════════════════
def ar(text):
    if not text:
        return ""
    return str(text)
# ══════════════════════════════════════════════════════════════════════════
# METRIC CARD
# ═══════════════════════════════════════════════════════════════════════════

def metric_card(value, label, accent_color=None, bg=None):
    """
    Build a single KPI metric card (Table-based).
    
    Args:
        value: The metric value (number, string, etc.)
        label: The metric label (will be passed through ar())
        accent_color: Color for the value text (default: PRIMARY_BLUE)
        bg: Background color (default: WHITE)
    
    Returns:
        Table: A ReportLab Table object.
    """
    if accent_color is None:
        accent_color = PRIMARY_BLUE
    if bg is None:
        bg = WHITE
    
    data = [
        [Paragraph(str(value), ParagraphStyle(
            'mv', fontName=FONT_BOLD, fontSize=18,
            textColor=accent_color, alignment=TA_CENTER, leading=22))],
        [Paragraph(ar(label), ParagraphStyle(
            'ml', fontName=FONT_MEDIUM, fontSize=8,
            textColor=MUTED, alignment=TA_CENTER, leading=11))],
    ]
    t = Table(data, colWidths=[3.8 * cm], rowHeights=[1.1 * cm, 0.8 * cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bg),
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    return t


# ══════════════════════════════════════════════════════════════════════════
# BADGE ELEMENT
# ═══════════════════════════════════════════════════════════════════════════

def badge_element(text, bg_color):
    """
    Build a small colored badge (e.g., "SEVERE", "J93.9").
    
    Args:
        text: Badge text (will be uppercased)
        bg_color: Background color for the badge
    
    Returns:
        Table: A ReportLab Table object.
    """
    style = ParagraphStyle('badge', fontName=FONT_BOLD, fontSize=7.5,
                           textColor=WHITE, alignment=TA_CENTER, leading=10)
    data = [[Paragraph(str(text).upper(), style)]]
    t = Table(data, colWidths=[2 * cm], rowHeights=[0.5 * cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bg_color),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    return t


# ═══════════════════════════════════════════════════════════════════════════
# QR CODE
# ═══════════════════════════════════════════════════════════════════════════

def build_qr_code(data_text, size=2 * cm):
    """
    Build a QR code Drawing, or a vector fallback if qrcode library is missing.
    
    Args:
        data_text: The text/URL to encode in the QR code
        size: Size of the QR code (default: 2 cm)
    
    Returns:
        Drawing: A ReportLab Drawing object.
    """
    if QR_AVAILABLE:
        try:
            qr = _qrcode_module.QRCode(box_size=3, border=1)
            qr.add_data(data_text)
            qr.make(fit=True)
            matrix = qr.get_matrix()
            n = len(matrix)
            cell = size / n
            d = Drawing(size, size)
            d.add(Rect(0, 0, size, size, fillColor=WHITE,
                       strokeColor=BORDER_GRAY, strokeWidth=0.5))
            for r_idx, row in enumerate(matrix):
                for c_idx, val in enumerate(row):
                    if val:
                        d.add(Rect(c_idx * cell, size - (r_idx + 1) * cell,
                                   cell, cell, fillColor=INK, strokeColor=None))
            return d
        except Exception:
            pass
    
    # Vector fallback — checkered pattern resembling a QR
    d = Drawing(size, size)
    d.add(Rect(0, 0, size, size, fillColor=WHITE, strokeColor=BORDER_GRAY, strokeWidth=0.8))
    cells = 5
    cell = size / cells
    pattern = [(0,0),(1,0),(2,0),(3,0),(4,0),(0,4),(1,4),(2,4),(3,4),(4,4),
                (0,1),(0,2),(0,3),(4,1),(4,2),(4,3),(2,2)]
    for col, row in pattern:
        d.add(Rect(col * cell + 1, row * cell + 1,
                   cell - 2, cell - 2, fillColor=INK, strokeColor=None))
    d.add(String(size / 2, size / 2 - 3, "QR",
                 fontName=FONT_BOLD, fontSize=8, fillColor=MUTED, textAnchor='middle'))
    return d


# ═══════════════════════════════════════════════════════════════════════════
# SECTION DIVIDER
# ═══════════════════════════════════════════════════════════════════════════

def section_divider(number, title, icon_name="summary"):
    """
    Build a section divider with number badge, title, and icon.
    
    Args:
        number: Section number (string or int)
        title: Section title (will be passed through ar())
        icon_name: Icon name from icons.py
    
    Returns:
        Table: A ReportLab Table object.
    """
    num_cell = Table([[Paragraph(str(number), ParagraphStyle(
        'sn', fontName=FONT_BOLD, fontSize=11,
        textColor=WHITE, alignment=TA_CENTER, leading=14))]],
        colWidths=[0.9 * cm], rowHeights=[0.9 * cm])
    num_cell.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), PRIMARY_BLUE),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    title_para = Paragraph(ar(title), ParagraphStyle(
        'st', fontName=FONT_BOLD, fontSize=13,
        textColor=PRIMARY_BLUE, alignment=TA_RIGHT, leading=17))
    icon_cell = vector_icon(icon_name, 0.7 * cm, PRIMARY_BLUE)
    
    divider = Table([[icon_cell, title_para, num_cell]],
                    colWidths=[0.9 * cm, 13.9 * cm, 1.2 * cm])
    divider.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, PRIMARY_BLUE),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    return divider


# ═══════════════════════════════════════════════════════════════════════════
# VERIFICATION HASH
# ═══════════════════════════════════════════════════════════════════════════

def compute_verification_hash(report_id, results, timestamp):
    """
    Compute a SHA-256 verification hash for the report.
    
    Args:
        report_id: Unique report ID
        results: List of result dicts (must have 'disease' and 'probability' keys)
        timestamp: ISO timestamp string
    
    Returns:
        str: First 20 characters of the uppercase hex digest.
    """
    payload = f"{report_id}|{timestamp}|{len(results)}|"
    payload += "|".join(f"{r['disease']}:{r['probability']}" for r in results)
    return hashlib.sha256(payload.encode('utf-8')).hexdigest().upper()[:20]


# ═══════════════════════════════════════════════════════════════════════════
# HEADER / FOOTER
# ═══════════════════════════════════════════════════════════════════════════

def header_footer(canvas, doc, logo_path=None):
    """
    Draw header and footer on every page.
    
    This function is designed to be passed as onFirstPage and onLaterPages
    to SimpleDocTemplate.build().
    
    Args:
        canvas: ReportLab canvas object
        doc: ReportLab document object
        logo_path: Optional path to logo image for watermark
    """
    canvas.saveState()
    w, h = A4
    
    # Optional watermark logo
    if logo_path and os.path.exists(logo_path):
        try:
            from reportlab.lib.utils import ImageReader
            img = ImageReader(logo_path)
            wm = 8 * cm
            canvas.saveState()
            canvas.setFillAlpha(0.04)
            canvas.drawImage(img, (w - wm) / 2, (h - wm) / 2 - 1 * cm,
                             width=wm, height=wm, mask='auto')
            canvas.restoreState()
        except Exception:
            pass
    
    # Top accent bars
    canvas.setFillColor(PRIMARY_BLUE)
    canvas.rect(0, h - 7, w, 7, fill=1, stroke=0)
    canvas.setFillColor(ACCENT_BLUE)
    canvas.rect(0, h - 9, w, 2, fill=1, stroke=0)
    
    # Footer rule
    canvas.setStrokeColor(LINE_GRAY)
    canvas.setLineWidth(0.5)
    canvas.line(2 * cm, 2.2 * cm, w - 2 * cm, 2.2 * cm)
    
    # Footer text
    canvas.setFont(FONT_REGULAR, 7)
    canvas.setFillColor(MUTED)
    canvas.drawString(2 * cm, 1.5 * cm, "RespAI\u2122  \u2022  AI-powered Chest X-ray Analysis")
    canvas.drawCentredString(w / 2, 1.5 * cm, "Confidential  \u2022  ISO Ready")
    canvas.drawRightString(w - 2 * cm, 1.5 * cm, f"Page {canvas.getPageNumber()}")
    canvas.drawCentredString(w / 2, 0.95 * cm, "Generated by RespAI Diagnostic System")
    
    canvas.restoreState()