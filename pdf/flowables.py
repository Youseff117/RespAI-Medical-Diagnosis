"""
Custom "Flowables" for PDF Report (HTML/CSS/SVG version)
============================================================
Contains the HTML/SVG equivalents of the original ReportLab Flowables:
- gradient_progress_bar()  (was GradientProgressBar)
- risk_gauge()              (was RiskGauge)
- star_rating()              (was StarRating)

Each function returns a ready-to-embed HTML string.
"""

import math

from .config import ACCENT_BLUE, STATUS_ACCENT


def gradient_progress_bar(percentage, color_key='green', width='100%', height='10px'):
    """
    Build a simple horizontal progress bar (no text inside).

    Args:
        percentage: 0-100
        color_key: key into STATUS_ACCENT ('green'/'yellow'/'orange'/'red')
        width: CSS width (e.g. '100%' or '200px')
        height: CSS height (e.g. '10px')

    Returns:
        str: HTML snippet.
    """
    pct = max(0.0, min(100.0, float(percentage)))
    accent = STATUS_ACCENT.get(color_key, ACCENT_BLUE)
    return (
        f'<div class="progress-track" style="width:{width};height:{height};">'
        f'<div class="progress-fill" style="width:{pct}%;background:{accent};"></div>'
        f'</div>'
    )


def risk_gauge(percentage, color_hex, label, size=90):
    """
    Build a circular gauge (SVG) showing overall risk level, ~270deg arc.

    Args:
        percentage: 0-100
        color_hex: accent color for the value arc
        label: label text under the percentage
        size: size in px

    Returns:
        str: HTML/SVG snippet.
    """
    pct = max(0.0, min(100.0, float(percentage)))
    s = 100  # internal coordinate space
    cx, cy = s / 2, s / 2
    r = s * 0.38
    stroke_w = s * 0.13
    circumference = 2 * math.pi * r
    # 270-degree arc (75% of full circle), starting at -225deg (i.e. bottom-left)
    arc_fraction = 0.75
    arc_len = circumference * arc_fraction
    value_len = arc_len * (pct / 100.0)

    return f"""
<div style="width:{size}px;height:{size}px;display:inline-block;text-align:center;">
  <svg width="{size}" height="{size}" viewBox="0 0 {s} {s}" xmlns="http://www.w3.org/2000/svg">
    <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#E5E7EB" stroke-width="{stroke_w}"
            stroke-dasharray="{arc_len} {circumference}" stroke-dashoffset="0"
            transform="rotate(135 {cx} {cy})" stroke-linecap="round"/>
    <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color_hex}" stroke-width="{stroke_w}"
            stroke-dasharray="{value_len} {circumference}" stroke-dashoffset="0"
            transform="rotate(135 {cx} {cy})" stroke-linecap="round"/>
    <text x="{cx}" y="{cy - 2}" text-anchor="middle" font-size="{s*0.17}"
          font-weight="bold" fill="{color_hex}">{int(pct)}%</text>
    <text x="{cx}" y="{cy + s*0.16}" text-anchor="middle" font-size="{s*0.09}"
          fill="#5B6B80">{label}</text>
  </svg>
</div>"""


def star_rating(score, max_score=100, star_px=14):
    """
    Build a 5-star visual rating (full/half/empty stars) as HTML/CSS.

    Args:
        score: current score
        max_score: max possible score (default 100)
        star_px: font-size of each star in px

    Returns:
        str: HTML snippet.
    """
    stars_full = (score / max_score) * 5 if max_score else 0
    stars_html = []
    for i in range(5):
        fill_pct = max(0.0, min(1.0, stars_full - i)) * 100
        stars_html.append(
            f'<span class="star" style="width:{star_px}px;font-size:{star_px}px;">'
            f'&#9733;<span class="star-fill" style="width:{fill_pct}%;">&#9733;</span>'
            f'</span>'
        )
    return f'<span class="star-rating">{"".join(stars_html)}</span>'