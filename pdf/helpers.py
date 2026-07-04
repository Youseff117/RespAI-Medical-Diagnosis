"""
Helper Functions for PDF Generation (HTML/WeasyPrint version)
=================================================================

This module contains utility functions used throughout the PDF report generation:
- Arabic text passthrough (WeasyPrint's Pango-based text layout handles
  Arabic shaping + bidi natively, so no manual reshaping is needed anymore)
- Metric cards, badges, QR codes
- Section dividers
- Running page-header bar (top accent bars, repeated on every page via CSS)
- Verification hash computation

Dependencies:
- config.py (for colors, constants)
- styles.py (for fonts)
- icons.py (for vector icons)
"""

import base64
import hashlib
from io import BytesIO

from .config import PRIMARY_BLUE, MUTED, WHITE
from .icons import vector_icon

# ── Optional QR code library ────────────────────────────────────────────────
try:
    import qrcode as _qrcode_module
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False


# ══════════════════════════════════════════════════════════════════════════
# ARABIC TEXT HELPER
# ═══════════════════════════════════════════════════════════════════════════
def ar(text):
    """
    Passthrough for Arabic text.

    Unlike ReportLab (which needs arabic_reshaper + python-bidi to manually
    reshape/reorder Arabic glyphs), WeasyPrint renders text through Pango,
    which performs correct Arabic shaping and bidi reordering automatically
    as long as the surrounding HTML has dir="rtl" / lang="ar". So this
    function is kept only for API/call-site compatibility.
    """
    if not text:
        return ""
    return str(text)


# ══════════════════════════════════════════════════════════════════════════
# METRIC CARD
# ═══════════════════════════════════════════════════════════════════════════

def metric_card(value, label, accent_color=None, bg=None):
    """
    Build a single KPI metric card.

    Returns:
        str: HTML snippet (<div class="metric-card">...).
    """
    if accent_color is None:
        accent_color = PRIMARY_BLUE
    if bg is None:
        bg = WHITE
    return (
        f'<div class="metric-card" style="background:{bg};">'
        f'<div class="value" style="color:{accent_color};">{value}</div>'
        f'<div class="label">{ar(label)}</div>'
        f'</div>'
    )


# ══════════════════════════════════════════════════════════════════════════
# BADGE ELEMENT
# ═══════════════════════════════════════════════════════════════════════════

def badge_element(text, bg_color):
    """
    Build a small colored badge (e.g., "SEVERE", "J93.9").

    Returns:
        str: HTML snippet.
    """
    return f'<span class="badge" style="background:{bg_color};">{str(text).upper()}</span>'


# ═══════════════════════════════════════════════════════════════════════════
# QR CODE
# ═══════════════════════════════════════════════════════════════════════════

def build_qr_code(data_text, size_px=80):
    """
    Build a QR code as a base64-embedded <img>, or an SVG checkerboard
    fallback if the `qrcode` library is unavailable.

    Returns:
        str: HTML snippet.
    """
    if QR_AVAILABLE:
        try:
            qr = _qrcode_module.QRCode(box_size=8, border=1)
            qr.add_data(data_text)
            qr.make(fit=True)
            img = qr.make_image(fill_color="#1A2332", back_color="white")
            buf = BytesIO()
            img.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode("ascii")
            return (f'<img src="data:image/png;base64,{b64}" '
                    f'width="{size_px}" height="{size_px}" alt="QR" '
                    f'style="border:0.5pt solid #E3E8F0;"/>')
        except Exception:
            pass

    # Vector fallback — simple checkered pattern resembling a QR
    cells = 5
    cell = 100 / cells
    pattern = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (0, 4), (1, 4), (2, 4), (3, 4), (4, 4),
               (0, 1), (0, 2), (0, 3), (4, 1), (4, 2), (4, 3), (2, 2)]
    rects = "".join(
        f'<rect x="{c*cell+1}" y="{r*cell+1}" width="{cell-2}" height="{cell-2}" fill="#1A2332"/>'
        for c, r in pattern
    )
    return (f'<svg width="{size_px}" height="{size_px}" viewBox="0 0 100 100" '
            f'xmlns="http://www.w3.org/2000/svg">'
            f'<rect x="0" y="0" width="100" height="100" fill="white" stroke="#E3E8F0"/>'
            f'{rects}</svg>')


# ═══════════════════════════════════════════════════════════════════════════
# SECTION DIVIDER
# ═══════════════════════════════════════════════════════════════════════════

def section_divider(number, title, icon_name="summary"):
    """
    Build a section divider with number badge, title, and icon.

    Returns:
        str: HTML snippet.
    """
    icon_html = vector_icon(icon_name, 26, PRIMARY_BLUE)
    return (
        f'<div class="section-divider">'
        f'<div class="divider-icon">{icon_html}</div>'
        f'<div class="divider-title">{ar(title)}</div>'
        f'<div class="num-badge">{number}</div>'
        f'</div>'
    )


# ═══════════════════════════════════════════════════════════════════════════
# VERIFICATION HASH
# ═══════════════════════════════════════════════════════════════════════════

def compute_verification_hash(report_id, results, timestamp):
    """
    Compute a SHA-256 verification hash for the report. Unchanged from the
    original implementation.

    Returns:
        str: First 20 characters of the uppercase hex digest.
    """
    payload = f"{report_id}|{timestamp}|{len(results)}|"
    payload += "|".join(f"{r['disease']}:{r['probability']}" for r in results)
    return hashlib.sha256(payload.encode('utf-8')).hexdigest().upper()[:20]


# ═══════════════════════════════════════════════════════════════════════════
# PAGE HEADER BAR (repeated on every page via CSS `position: running(...)`)
# ═══════════════════════════════════════════════════════════════════════════

def page_header_bar_html():
    """
    HTML for the running page-header element (top accent bars). This element
    is placed once near the top of <body>; the CSS `position: running(...)`
    + `@top-center { content: element(...) }` rule in styles.py causes
    WeasyPrint to repeat it at the top margin of every page, replacing the
    manual per-page canvas drawing used in the ReportLab version.

    Returns:
        str: HTML snippet.
    """
    return (
        '<div id="page-header-bar">'
        '<div class="header-bar-track"></div>'
        '<div class="header-bar-accent"></div>'
        '</div>'
    )