"""
Styles and Font Registration
=============================

This module handles:
- Cairo fonts registration with fallback to Helvetica
- All paragraph styles used in the PDF report (Arabic + English)

Dependencies:
- config.py (for colors)
"""

import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY

from .config import (
    PRIMARY_BLUE, MUTED, INK, WHITE,
)

# ═══════════════════════════════════════════════════════════════════════════
# FONT REGISTRATION (with graceful fallback)
# ═══════════════════════════════════════════════════════════════════════════

FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "fonts")
FONT_FILES = {
    "Cairo":          "Cairo-Regular.ttf",
    "Cairo-Bold":     "Cairo-Bold.ttf",
    "Cairo-SemiBold": "Cairo-SemiBold.ttf",
    "Cairo-Medium":   "Cairo-Medium.ttf",
}

CAIRO_AVAILABLE = False
for _fn, _file in FONT_FILES.items():
    _path = os.path.join(FONT_DIR, _file)
    if os.path.exists(_path):
        try:
            pdfmetrics.registerFont(TTFont(_fn, _path))
            CAIRO_AVAILABLE = True
        except Exception:
            pass


def _font(cairo_name, bold=False):
    """
    Return Cairo font name if registered, else Helvetica fallback.
    
    This ensures the PDF can be generated even if Cairo fonts are missing,
    though Arabic text won't render properly without Cairo.
    """
    if CAIRO_AVAILABLE:
        return cairo_name
    return "Helvetica-Bold" if bold else "Helvetica"


# Pre-resolved font names (used throughout the codebase)
FONT_REGULAR   = _font("Cairo")
FONT_BOLD      = _font("Cairo-Bold",     bold=True)
FONT_SEMIBOLD  = _font("Cairo-SemiBold", bold=True)
FONT_MEDIUM    = _font("Cairo-Medium")


# ═══════════════════════════════════════════════════════════════════════════
# STYLES DEFINITION
# ═══════════════════════════════════════════════════════════════════════════

def get_custom_styles():
    """
    Build and return the complete stylesheet for the PDF report.
    
    Returns:
        StyleSheet1: ReportLab stylesheet with all custom paragraph styles.
    
    Style naming convention:
        - Arabic*  : Right-aligned Arabic text
        - English* : Left-aligned English text
        - Disclaimer: Red-tinted legal text
    """
    styles = getSampleStyleSheet()
    
    # Style definitions: (name, font, size, color, alignment, spaceAfter, leading)
    defs = [
        # Arabic styles (RTL)
        ('ArabicTitle',          FONT_BOLD,      22, PRIMARY_BLUE,  TA_CENTER,   6,  28),
        ('ArabicSubtitle',       FONT_MEDIUM,    12, MUTED,         TA_CENTER,   8,  16),
        ('ArabicHeading',        FONT_BOLD,      13, PRIMARY_BLUE,  TA_RIGHT,    6,  17),
        ('ArabicSubheading',     FONT_SEMIBOLD,  11, INK,           TA_RIGHT,    4,  15),
        ('ArabicBody',           FONT_REGULAR,   10, INK,           TA_RIGHT,    3,  15),
        ('ArabicBodyJustify',    FONT_REGULAR,   10, INK,           TA_JUSTIFY,  3,  15),
        ('ArabicSmall',          FONT_REGULAR,    9, MUTED,         TA_RIGHT,    2,  13),
        ('ArabicTiny',           FONT_REGULAR,    8, MUTED,         TA_CENTER,   2,  11),
        
        # Table styles
        ('ArabicTableHeader',    FONT_BOLD,       9, WHITE,         TA_CENTER,   0,  13),
        ('ArabicTableCell',      FONT_MEDIUM,     9, INK,           TA_CENTER,   0,  13),
        ('ArabicTableCellRight', FONT_MEDIUM,     9, INK,           TA_RIGHT,    0,  13),
        
        # English styles (LTR)
        ('EnglishBody',          FONT_REGULAR,   10, INK,           TA_LEFT,     3,  14),
        ('EnglishSmall',         FONT_REGULAR,    8, MUTED,         TA_LEFT,     2,  11),
        ('EnglishBold',          FONT_BOLD,      10, INK,           TA_LEFT,     3,  14),
        
        # Special styles
        ('Disclaimer',           FONT_REGULAR,    9, 
         colors.HexColor('#7A1F1F'), TA_JUSTIFY, 3,  13),
    ]
    
    for name, font, size, clr, align, after, lead in defs:
        # Avoid duplicate style errors
        if name not in styles:
            styles.add(ParagraphStyle(
                name=name,
                fontName=font,
                fontSize=size,
                textColor=clr,
                alignment=align,
                spaceAfter=after,
                leading=lead,
            ))
    
    return styles


# ═══════════════════════════════════════════════════════════════════════════
# CONVENIENCE: Import colors for the Disclaimer style
# ═══════════════════════════════════════════════════════════════════════════
from reportlab.lib import colors