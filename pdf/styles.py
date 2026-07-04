"""
Styles: CSS Generation for WeasyPrint
=======================================

This module replaces the old ReportLab font-registration / ParagraphStyle
system with a single CSS stylesheet used by WeasyPrint.

- Registers the Cairo Arabic font family (with graceful fallback) via @font-face.
- Defines @page rules (size, margins, running header bar, footer with page numbers).
- Defines utility classes that mirror the old ParagraphStyle names so the rest
  of the codebase (components.py / sections.py) can keep familiar naming.

Dependencies:
- config.py (for colors)
"""

import os

from .config import (
    PRIMARY_BLUE, SECONDARY_BLUE, ACCENT_BLUE, SOFT_BLUE, ULTRA_LIGHT,
    INK, MUTED, LINE_GRAY, BORDER_GRAY, WHITE, PAGE_BG,
    LOGO_BLUE, LOGO_CYAN,
)

# ═══════════════════════════════════════════════════════════════════════════
# FONT DISCOVERY (Cairo, with graceful fallback to system fonts)
# ═══════════════════════════════════════════════════════════════════════════

FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "fonts")
FONT_FILES = {
    "Cairo":          "Cairo-Regular.ttf",
    "Cairo-Bold":     "Cairo-Bold.ttf",
    "Cairo-SemiBold": "Cairo-SemiBold.ttf",
    "Cairo-Medium":   "Cairo-Medium.ttf",
}

CAIRO_AVAILABLE = any(
    os.path.exists(os.path.join(FONT_DIR, fname)) for fname in FONT_FILES.values()
)

# Font family names used throughout the stylesheet. If the Cairo TTFs are not
# found on disk, WeasyPrint will simply fall back to the generic families
# below (still fully capable of Arabic shaping via the system's Pango/Fontconfig
# stack, unlike ReportLab which required manual reshaping).
FONT_REGULAR  = "Cairo" if CAIRO_AVAILABLE else "'Noto Sans Arabic', Tahoma, sans-serif"
FONT_BOLD     = "Cairo-Bold" if CAIRO_AVAILABLE else "'Noto Sans Arabic', Tahoma, sans-serif"
FONT_SEMIBOLD = "Cairo-SemiBold" if CAIRO_AVAILABLE else "'Noto Sans Arabic', Tahoma, sans-serif"
FONT_MEDIUM   = "Cairo-Medium" if CAIRO_AVAILABLE else "'Noto Sans Arabic', Tahoma, sans-serif"


def _font_face_rules():
    if not CAIRO_AVAILABLE:
        return ""
    rules = []
    for family, fname in FONT_FILES.items():
        path = os.path.join(FONT_DIR, fname)
        if os.path.exists(path):
            # Use a path relative to the project root (base_url passed to WeasyPrint)
            rel_path = os.path.join("static", "fonts", fname).replace("\\", "/")
            weight = "bold" if family in ("Cairo-Bold",) else "normal"
            rules.append(f"""
@font-face {{
    font-family: '{family}';
    src: url('{rel_path}') format('truetype');
    font-weight: {weight};
    font-style: normal;
}}""")
    return "\n".join(rules)


# ═══════════════════════════════════════════════════════════════════════════
# MAIN STYLESHEET
# ═══════════════════════════════════════════════════════════════════════════

def get_css() -> str:
    """
    Build and return the complete CSS stylesheet for the PDF report.

    Returns:
        str: A <style> block's worth of CSS.
    """
    return f"""
{_font_face_rules()}

@page {{
    size: A4;
    margin: 2.9cm 2cm 2.6cm 2cm;

    @top-center {{
        content: element(pageHeaderBar);
    }}
    @bottom-left {{
        content: "RespAI\\2122  \\2022  AI-powered Chest X-ray Analysis";
        font-family: {FONT_REGULAR};
        font-size: 7pt;
        color: {MUTED};
    }}
    @bottom-center {{
        content: "Confidential \\2022 ISO Ready";
        font-family: {FONT_REGULAR};
        font-size: 7pt;
        color: {MUTED};
    }}
    @bottom-right {{
        content: "Page " counter(page);
        font-family: {FONT_REGULAR};
        font-size: 7pt;
        color: {MUTED};
    }}
}}

@page :first {{
    @top-center {{ content: element(pageHeaderBar); }}
}}

* {{ box-sizing: border-box; }}

html {{ direction: rtl; }}

body {{
    font-family: {FONT_REGULAR};
    font-size: 10pt;
    color: {INK};
    background: {WHITE};
    direction: rtl;
    margin: 0;
    padding: 0;
}}

/* Running page-header bar (rendered once, repeated on every page via @top-center) */
#page-header-bar {{
    position: running(pageHeaderBar);
}}
.header-bar-track {{
    width: 100%;
    height: 7px;
    background: linear-gradient(90deg, {LOGO_BLUE}, {LOGO_CYAN});
}}
.header-bar-accent {{
    width: 100%;
    height: 2px;
    background: {ACCENT_BLUE};
}}

/* ── Page-break helpers ─────────────────────────────────────────────── */
.page-break {{ break-before: page; }}
.avoid-break {{ break-inside: avoid; }}

/* ── Typography (mirrors old ReportLab ParagraphStyle names) ──────────── */
.arabic-title {{ font-family: {FONT_BOLD}; font-size: 22pt; color: {PRIMARY_BLUE}; text-align: center; line-height: 1.3; margin: 0 0 6pt 0; }}
.arabic-subtitle {{ font-family: {FONT_MEDIUM}; font-size: 12pt; color: {MUTED}; text-align: center; line-height: 1.3; margin: 0 0 8pt 0; }}
.arabic-heading {{ font-family: {FONT_BOLD}; font-size: 13pt; color: {PRIMARY_BLUE}; text-align: right; line-height: 1.3; margin: 0 0 6pt 0; }}
.arabic-subheading {{ font-family: {FONT_SEMIBOLD}; font-size: 11pt; color: {INK}; text-align: right; line-height: 1.35; margin: 0 0 4pt 0; }}
.arabic-body {{ font-family: {FONT_REGULAR}; font-size: 10pt; color: {INK}; text-align: right; line-height: 1.5; margin: 0 0 3pt 0; }}
.arabic-body-justify {{ font-family: {FONT_REGULAR}; font-size: 10pt; color: {INK}; text-align: justify; line-height: 1.5; margin: 0 0 3pt 0; }}
.arabic-small {{ font-family: {FONT_REGULAR}; font-size: 9pt; color: {MUTED}; text-align: right; line-height: 1.4; margin: 0 0 2pt 0; }}
.arabic-tiny {{ font-family: {FONT_REGULAR}; font-size: 8pt; color: {MUTED}; text-align: center; line-height: 1.35; margin: 0 0 2pt 0; }}

.table-header {{ font-family: {FONT_BOLD}; font-size: 9pt; color: {WHITE}; text-align: center; }}
.table-cell {{ font-family: {FONT_MEDIUM}; font-size: 9pt; color: {INK}; text-align: center; }}
.table-cell-right {{ font-family: {FONT_MEDIUM}; font-size: 9pt; color: {INK}; text-align: right; }}

.english-body {{ font-family: {FONT_REGULAR}; font-size: 10pt; color: {INK}; text-align: left; direction: ltr; line-height: 1.4; margin: 0 0 3pt 0; }}
.english-small {{ font-family: {FONT_REGULAR}; font-size: 8pt; color: {MUTED}; text-align: left; direction: ltr; line-height: 1.35; margin: 0 0 2pt 0; }}
.english-bold {{ font-family: {FONT_BOLD}; font-size: 10pt; color: {INK}; text-align: left; direction: ltr; line-height: 1.4; margin: 0 0 3pt 0; }}

.disclaimer {{ font-family: {FONT_REGULAR}; font-size: 9pt; color: #7A1F1F; text-align: justify; line-height: 1.4; margin: 0 0 3pt 0; }}

/* ── Generic layout helpers ─────────────────────────────────────────── */
.section {{ margin-bottom: 0.4cm; }}
.spacer-sm {{ height: 0.15cm; }}
.spacer-md {{ height: 0.3cm; }}
.spacer-lg {{ height: 0.5cm; }}

.box {{
    background: {ULTRA_LIGHT};
    border: 0.5pt solid {LINE_GRAY};
    padding: 8pt 10pt;
}}

table.report-table {{ width: 100%; border-collapse: collapse; }}
table.report-table th, table.report-table td {{
    border: 0.4pt solid {LINE_GRAY};
    padding: 5pt 6pt;
    vertical-align: middle;
}}
table.report-table thead th {{
    background: {PRIMARY_BLUE};
    color: {WHITE};
    font-family: {FONT_BOLD};
    font-size: 9pt;
    text-align: center;
}}
table.report-table tbody tr:nth-child(even) {{ background: {ULTRA_LIGHT}; }}

table.plain-table {{ width: 100%; border-collapse: collapse; background: {ULTRA_LIGHT}; border: 0.6pt solid {LINE_GRAY}; }}
table.plain-table td {{ border: 0.4pt solid {LINE_GRAY}; padding: 6pt 8pt; vertical-align: middle; }}

.metric-cards {{ display: flex; gap: 6pt; justify-content: center; }}
.metric-card {{
    flex: 1;
    border: 0.5pt solid {BORDER_GRAY};
    text-align: center;
    padding: 6pt 4pt;
}}
.metric-card .value {{ font-family: {FONT_BOLD}; font-size: 15pt; line-height: 1.3; }}
.metric-card .label {{ font-family: {FONT_MEDIUM}; font-size: 8pt; color: {MUTED}; margin-top: 2pt; }}

.badge {{
    display: inline-block;
    font-family: {FONT_BOLD};
    font-size: 7.5pt;
    color: {WHITE};
    text-align: center;
    padding: 3pt 8pt;
    border-radius: 2pt;
}}

.progress-track {{
    width: 100%;
    background: #EEF2F7;
    border-radius: 6px;
    overflow: hidden;
}}
.progress-fill {{ height: 100%; border-radius: 6px; }}

.section-divider {{
    display: flex;
    align-items: center;
    border-bottom: 1.5pt solid {LOGO_CYAN};
    padding-bottom: 6pt;
    margin-bottom: 4pt;
}}
.section-divider .num-badge {{
    background: linear-gradient(135deg, {LOGO_BLUE}, {LOGO_CYAN});
    color: {WHITE};
    font-family: {FONT_BOLD};
    font-size: 11pt;
    width: 0.9cm;
    height: 0.9cm;
    line-height: 0.9cm;
    text-align: center;
    border-radius: 2pt;
    flex: 0 0 auto;
}}
.section-divider .divider-title {{
    flex: 1;
    font-family: {FONT_BOLD};
    font-size: 13pt;
    color: {PRIMARY_BLUE};
    text-align: right;
    padding: 0 8pt;
}}
.section-divider .divider-icon {{ flex: 0 0 auto; }}

.cover-page {{ text-align: center; padding-top: 0.5cm; }}
.confidential {{ font-family: {FONT_BOLD}; font-size: 10pt; color: #7A1F1F; text-align: center; }}

.pipeline-row {{ display: flex; gap: 2pt; justify-content: center; }}
.pipeline-step {{
    flex: 1;
    text-align: center;
    font-family: {FONT_BOLD};
    font-size: 7pt;
    padding: 6pt 2pt;
    border: 0.5pt solid {WHITE};
}}

.timeline-row {{ display: flex; gap: 2pt; justify-content: center; border-bottom: 0.3pt solid {LINE_GRAY}; padding-bottom: 4pt; }}
.timeline-step {{ flex: 1; text-align: center; }}
.timeline-step .step-name {{ font-family: {FONT_BOLD}; font-size: 8pt; color: {PRIMARY_BLUE}; }}
.timeline-step .step-time {{ font-family: {FONT_REGULAR}; font-size: 7pt; color: {MUTED}; }}

.doctor-note-line {{ border-bottom: 0.4pt solid {LINE_GRAY}; height: 0.55cm; margin-bottom: 0.1cm; }}

.star-rating {{ display: inline-flex; direction: ltr; }}
.star {{ position: relative; display: inline-block; width: 12pt; font-size: 12pt; line-height: 1; color: #D1D5DB; }}
.star .star-fill {{ position: absolute; top: 0; left: 0; overflow: hidden; color: #F59E0B; white-space: nowrap; }}
"""