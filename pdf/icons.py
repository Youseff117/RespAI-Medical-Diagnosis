"""
Vector Icons for PDF Report (SVG version)
===========================================

Same icon set and names as the original ReportLab implementation, redrawn as
inline SVG so WeasyPrint can render them directly inside the HTML document.
"""

from .config import PRIMARY_BLUE, SOFT_BLUE, STATUS_BG, STATUS_ACCENT, LOGO_BLUE, LOGO_CYAN

_HEATMAP_COLORS = [
    '#4CAF50', '#FFEB3B', '#FF9800',
    '#FFEB3B', '#F44336', '#FF9800',
    '#4CAF50', '#FF9800', '#FFEB3B',
]


def vector_icon(name, size=28, color=None):
    """
    Return an inline SVG icon string, in a 100x100 viewBox scaled to `size` px.

    Args:
        name: icon name (same set as the original module)
        size: rendered size in pixels (int or CSS length string)
        color: main stroke/fill color (default: PRIMARY_BLUE)

    Returns:
        str: an <svg>...</svg> string.
    """
    if color is None:
        color = PRIMARY_BLUE
    sz = f"{size}px" if isinstance(size, (int, float)) else size
    s = 100  # internal coordinate space

    body = ""

    if name == "logo":
        # RespAI brand mark: gradient squircle badge with "R+" monogram.
        # Used on the cover page and anywhere the actual brand icon (not a
        # generic pictogram) is needed.
        body = f"""
        <defs>
            <linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="{LOGO_BLUE}"/>
                <stop offset="100%" stop-color="{LOGO_CYAN}"/>
            </linearGradient>
        </defs>
        <rect x="0" y="0" width="{s}" height="{s}" rx="14" fill="url(#logoGrad)"/>
        <text x="{s*0.5}" y="{s*0.62}" font-family="Cairo-Bold, Arial, sans-serif"
              font-size="{s*0.42}" font-weight="700" fill="#FFFFFF"
              text-anchor="middle">R+</text>"""
    elif name == "summary":
        body = f"""
        <rect x="0" y="0" width="{s}" height="{s}" rx="6" fill="{SOFT_BLUE}" stroke="{color}" stroke-width="1.5"/>
        <rect x="{s*0.2}" y="{s*0.33}" width="{s*0.6}" height="{s*0.12}" fill="{color}"/>
        <rect x="{s*0.2}" y="{s*0.56}" width="{s*0.45}" height="{s*0.12}" fill="{color}"/>
        <rect x="{s*0.2}" y="{s*0.78}" width="{s*0.55}" height="{s*0.12}" fill="{color}"/>"""
    elif name == "patient":
        body = f"""
        <circle cx="{s/2}" cy="{s/2}" r="{s*0.45}" fill="{SOFT_BLUE}" stroke="{color}" stroke-width="1.5"/>
        <circle cx="{s/2}" cy="{s*0.42}" r="{s*0.14}" fill="{color}"/>
        <rect x="{s*0.28}" y="{s*0.60}" width="{s*0.44}" height="{s*0.22}" rx="4" fill="{color}"/>"""
    elif name == "findings":
        body = f"""
        <circle cx="{s/2}" cy="{s/2}" r="{s*0.45}" fill="{SOFT_BLUE}" stroke="{color}" stroke-width="1.5"/>
        <line x1="{s*0.2}" y1="{s*0.5}" x2="{s*0.8}" y2="{s*0.5}" stroke="{color}" stroke-width="3"/>
        <line x1="{s*0.5}" y1="{s*0.2}" x2="{s*0.5}" y2="{s*0.8}" stroke="{color}" stroke-width="3"/>"""
    elif name == "ai":
        body = f"""
        <rect x="{s*0.1}" y="{s*0.15}" width="{s*0.8}" height="{s*0.7}" rx="6" fill="{SOFT_BLUE}" stroke="{color}" stroke-width="1.5"/>
        <circle cx="{s*0.35}" cy="{s*0.5}" r="{s*0.07}" fill="{color}"/>
        <circle cx="{s*0.65}" cy="{s*0.5}" r="{s*0.07}" fill="{color}"/>
        <line x1="{s*0.3}" y1="{s*0.7}" x2="{s*0.7}" y2="{s*0.7}" stroke="{color}" stroke-width="2"/>"""
    elif name == "recommend":
        body = f"""
        <rect x="{s*0.15}" y="{s*0.05}" width="{s*0.7}" height="{s*0.9}" rx="4" fill="{SOFT_BLUE}" stroke="{color}" stroke-width="1.5"/>
        <line x1="{s*0.28}" y1="{s*0.3}" x2="{s*0.72}" y2="{s*0.3}" stroke="{color}" stroke-width="1.6"/>
        <line x1="{s*0.28}" y1="{s*0.5}" x2="{s*0.72}" y2="{s*0.5}" stroke="{color}" stroke-width="1.6"/>
        <line x1="{s*0.28}" y1="{s*0.7}" x2="{s*0.6}" y2="{s*0.7}" stroke="{color}" stroke-width="1.6"/>"""
    elif name == "warning":
        body = f"""
        <polygon points="{s*0.5},{s*0.1} {s*0.95},{s*0.95} {s*0.05},{s*0.95}" fill="#FFF1E6" stroke="#D97706" stroke-width="1.6"/>
        <line x1="{s*0.5}" y1="{s*0.4}" x2="{s*0.5}" y2="{s*0.7}" stroke="#D97706" stroke-width="3"/>
        <circle cx="{s*0.5}" cy="{s*0.82}" r="{s*0.045}" fill="#D97706"/>"""
    elif name == "doctor":
        body = f"""
        <circle cx="{s/2}" cy="{s*0.32}" r="{s*0.22}" fill="{SOFT_BLUE}" stroke="{color}" stroke-width="1.5"/>
        <rect x="{s*0.18}" y="{s*0.55}" width="{s*0.64}" height="{s*0.4}" rx="4" fill="{SOFT_BLUE}" stroke="{color}" stroke-width="1.5"/>
        <line x1="{s*0.5}" y1="{s*0.6}" x2="{s*0.5}" y2="{s*0.85}" stroke="{color}" stroke-width="2"/>
        <line x1="{s*0.38}" y1="{s*0.72}" x2="{s*0.62}" y2="{s*0.72}" stroke="{color}" stroke-width="2"/>"""
    elif name == "chart":
        body = f"""
        <rect x="0" y="0" width="{s}" height="{s}" rx="6" fill="{SOFT_BLUE}" stroke="{color}" stroke-width="1.5"/>
        <rect x="{s*0.15}" y="{s*0.5}" width="{s*0.15}" height="{s*0.35}" fill="{color}"/>
        <rect x="{s*0.4}" y="{s*0.25}" width="{s*0.15}" height="{s*0.6}" fill="{color}"/>
        <rect x="{s*0.65}" y="{s*0.38}" width="{s*0.15}" height="{s*0.47}" fill="{color}"/>"""
    elif name == "tech":
        body = f"""
        <rect x="{s*0.1}" y="{s*0.1}" width="{s*0.8}" height="{s*0.8}" rx="6" fill="{SOFT_BLUE}" stroke="{color}" stroke-width="1.5"/>
        <circle cx="{s*0.5}" cy="{s*0.5}" r="{s*0.2}" fill="none" stroke="{color}" stroke-width="1.6"/>
        <circle cx="{s*0.5}" cy="{s*0.5}" r="{s*0.07}" fill="{color}"/>"""
    elif name == "stats":
        body = f"""
        <rect x="0" y="0" width="{s}" height="{s}" rx="6" fill="{SOFT_BLUE}" stroke="{color}" stroke-width="1.5"/>
        <line x1="{s*0.15}" y1="{s*0.15}" x2="{s*0.15}" y2="{s*0.85}" stroke="{color}" stroke-width="2"/>
        <line x1="{s*0.15}" y1="{s*0.85}" x2="{s*0.85}" y2="{s*0.85}" stroke="{color}" stroke-width="2"/>
        <rect x="{s*0.25}" y="{s*0.55}" width="{s*0.12}" height="{s*0.28}" fill="{color}"/>
        <rect x="{s*0.45}" y="{s*0.35}" width="{s*0.12}" height="{s*0.48}" fill="{color}"/>
        <rect x="{s*0.65}" y="{s*0.45}" width="{s*0.12}" height="{s*0.38}" fill="{color}"/>"""
    elif name == "shield":
        body = f"""
        <polygon points="{s*0.5},{s*0.05} {s*0.9},{s*0.25} {s*0.9},{s*0.6} {s*0.5},{s*0.95} {s*0.1},{s*0.6} {s*0.1},{s*0.25}"
                 fill="{SOFT_BLUE}" stroke="{color}" stroke-width="1.6"/>
        <polyline points="{s*0.35},{s*0.55} {s*0.48},{s*0.68} {s*0.68},{s*0.42}" fill="none" stroke="{color}" stroke-width="3"/>"""
    elif name == "book":
        body = f"""
        <rect x="{s*0.1}" y="{s*0.1}" width="{s*0.8}" height="{s*0.8}" rx="2" fill="{SOFT_BLUE}" stroke="{color}" stroke-width="1.5"/>
        <line x1="{s*0.5}" y1="{s*0.15}" x2="{s*0.5}" y2="{s*0.85}" stroke="{color}" stroke-width="1.6"/>
        <line x1="{s*0.15}" y1="{s*0.35}" x2="{s*0.45}" y2="{s*0.35}" stroke="{color}" stroke-width="1"/>
        <line x1="{s*0.15}" y1="{s*0.5}" x2="{s*0.45}" y2="{s*0.5}" stroke="{color}" stroke-width="1"/>
        <line x1="{s*0.15}" y1="{s*0.65}" x2="{s*0.45}" y2="{s*0.65}" stroke="{color}" stroke-width="1"/>"""
    elif name == "normal":
        gc = STATUS_ACCENT['green']
        body = f"""
        <circle cx="{s/2}" cy="{s/2}" r="{s*0.45}" fill="{STATUS_BG['green']}" stroke="{gc}" stroke-width="2"/>
        <polyline points="{s*0.3},{s*0.5} {s*0.45},{s*0.65} {s*0.7},{s*0.38}" fill="none" stroke="{gc}" stroke-width="3"/>"""
    elif name == "hospital":
        body = f"""
        <rect x="{s*0.1}" y="{s*0.2}" width="{s*0.8}" height="{s*0.7}" rx="6" fill="{SOFT_BLUE}" stroke="{color}" stroke-width="1.5"/>
        <line x1="{s*0.5}" y1="{s*0.35}" x2="{s*0.5}" y2="{s*0.75}" stroke="{color}" stroke-width="3"/>
        <line x1="{s*0.3}" y1="{s*0.55}" x2="{s*0.7}" y2="{s*0.55}" stroke="{color}" stroke-width="3"/>
        <rect x="{s*0.35}" y="{s*0.05}" width="{s*0.3}" height="{s*0.15}" fill="{SOFT_BLUE}" stroke="{color}" stroke-width="1.5"/>"""
    elif name == "quality":
        body = f"""
        <rect x="0" y="0" width="{s}" height="{s}" rx="6" fill="{SOFT_BLUE}" stroke="{color}" stroke-width="1.5"/>
        <circle cx="{s*0.5}" cy="{s*0.5}" r="{s*0.3}" fill="none" stroke="{color}" stroke-width="1.6"/>
        <circle cx="{s*0.5}" cy="{s*0.5}" r="{s*0.12}" fill="{color}"/>"""
    elif name == "confidence":
        body = f"""
        <rect x="0" y="0" width="{s}" height="{s}" rx="6" fill="{SOFT_BLUE}" stroke="{color}" stroke-width="1.5"/>
        <polygon points="{s*0.5},{s*0.15} {s*0.85},{s*0.5} {s*0.5},{s*0.85} {s*0.15},{s*0.5}" fill="none" stroke="{color}" stroke-width="1.6"/>
        <circle cx="{s*0.5}" cy="{s*0.5}" r="{s*0.08}" fill="{color}"/>"""
    elif name == "heatmap":
        cells = ""
        cell = s / 3
        for idx in range(9):
            row, col = divmod(idx, 3)
            cells += (f'<rect x="{col*cell+s*0.05}" y="{row*cell+s*0.05}" '
                      f'width="{cell-s*0.04}" height="{cell-s*0.04}" fill="{_HEATMAP_COLORS[idx]}"/>')
        body = f'<rect x="0" y="0" width="{s}" height="{s}" rx="6" fill="{SOFT_BLUE}" stroke="{color}" stroke-width="1.5"/>{cells}'
    elif name == "compare":
        body = f"""
        <rect x="{s*0.05}" y="{s*0.15}" width="{s*0.4}" height="{s*0.7}" rx="4" fill="{SOFT_BLUE}" stroke="{color}" stroke-width="1.5"/>
        <rect x="{s*0.55}" y="{s*0.15}" width="{s*0.4}" height="{s*0.7}" rx="4" fill="{SOFT_BLUE}" stroke="{color}" stroke-width="1.5"/>"""
    elif name == "severity":
        bars = [('green', 0.7), ('yellow', 0.5), ('orange', 0.3), ('red', 0.1)]
        rects = "".join(
            f'<rect x="{s*0.15}" y="{s*(1-y-0.1)}" width="{s*0.7}" height="{s*0.1}" fill="{STATUS_ACCENT[c]}"/>'
            for c, y in bars
        )
        body = f'<rect x="0" y="0" width="{s}" height="{s}" rx="6" fill="{SOFT_BLUE}" stroke="{color}" stroke-width="1.5"/>{rects}'
    elif name == "timeline":
        dots = "".join(f'<circle cx="{s*cx}" cy="{s*0.5}" r="{s*0.08}" fill="{color}"/>' for cx in (0.2, 0.5, 0.8))
        body = f'<line x1="{s*0.1}" y1="{s*0.5}" x2="{s*0.9}" y2="{s*0.5}" stroke="{color}" stroke-width="2"/>{dots}'
    elif name == "pipeline":
        boxes = "".join(
            f'<rect x="{s*bx}" y="{s*0.3}" width="{s*0.2}" height="{s*0.4}" fill="{SOFT_BLUE}" stroke="{color}" stroke-width="1.5"/>'
            for bx in (0.05, 0.4, 0.75)
        )
        body = (boxes +
                f'<line x1="{s*0.25}" y1="{s*0.5}" x2="{s*0.4}" y2="{s*0.5}" stroke="{color}" stroke-width="2"/>'
                f'<line x1="{s*0.6}" y1="{s*0.5}" x2="{s*0.75}" y2="{s*0.5}" stroke="{color}" stroke-width="2"/>')
    else:
        body = f'<circle cx="{s/2}" cy="{s/2}" r="{s*0.4}" fill="{SOFT_BLUE}" stroke="{color}" stroke-width="1.5"/>'

    return f'<svg width="{sz}" height="{sz}" viewBox="0 0 {s} {s}" xmlns="http://www.w3.org/2000/svg">{body}</svg>'