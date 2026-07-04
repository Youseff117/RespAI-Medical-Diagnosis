"""
Chart Builders for PDF Report (SVG version)
==============================================

This module contains functions to build charts as inline SVG:
- build_pie_chart(): Risk distribution donut chart
- build_bar_chart(): Disease probability horizontal bar chart

Dependencies:
- config.py (for colors)
"""

import math

from .config import STATUS_ACCENT, ACCENT_BLUE, MUTED


def build_pie_chart(counts: dict, size_px=210) -> str:
    """
    Build a donut/pie chart (SVG) showing risk distribution.

    Args:
        counts: Dict with keys 'green', 'yellow', 'orange', 'red' and count values
        size_px: rendered size in pixels

    Returns:
        str: HTML/SVG snippet.
    """
    labels = [('green', 'Normal'), ('yellow', 'Low'), ('orange', 'Moderate'), ('red', 'High')]
    values = [max(counts.get(k, 0), 0.01) for k, _ in labels]
    total = sum(values)

    s = 200
    cx, cy = s / 2, s / 2 - 10
    r = 70

    slices = []
    legend = []
    start_angle = -90.0
    for (key, label), val in zip(labels, values):
        frac = val / total
        sweep = frac * 360.0
        end_angle = start_angle + sweep

        x1 = cx + r * math.cos(math.radians(start_angle))
        y1 = cy + r * math.sin(math.radians(start_angle))
        x2 = cx + r * math.cos(math.radians(end_angle))
        y2 = cy + r * math.sin(math.radians(end_angle))
        large_arc = 1 if sweep > 180 else 0

        color = STATUS_ACCENT[key]
        slices.append(
            f'<path d="M{cx},{cy} L{x1:.2f},{y1:.2f} A{r},{r} 0 {large_arc} 1 {x2:.2f},{y2:.2f} Z" '
            f'fill="{color}" stroke="#FFFFFF" stroke-width="1.5"/>'
        )
        legend.append(
            f'<span style="display:inline-flex;align-items:center;gap:4px;margin:0 6px;">'
            f'<span style="width:9px;height:9px;background:{color};display:inline-block;border-radius:2px;"></span>'
            f'<span style="font-size:8pt;color:{MUTED};">{label}</span></span>'
        )
        start_angle = end_angle

    legend_html = "".join(legend)
    return f"""
<div style="text-align:center;">
  <svg width="{size_px}" height="{size_px}" viewBox="0 0 {s} {s}" xmlns="http://www.w3.org/2000/svg">
    {''.join(slices)}
    <circle cx="{cx}" cy="{cy}" r="{r*0.55}" fill="#FFFFFF"/>
  </svg>
  <div style="direction:ltr;">{legend_html}</div>
</div>"""


def build_bar_chart(results: list, top_n: int = 8, width_px=280, height_px=210) -> str:
    """
    Build a horizontal bar chart (SVG) showing disease probabilities.

    Args:
        results: List of result dicts (must have 'disease' and 'probability' keys)
        top_n: Number of top diseases to show (default: 8)
        width_px: rendered width in pixels
        height_px: rendered height in pixels

    Returns:
        str: HTML/SVG snippet.
    """
    sorted_res = sorted(results, key=lambda x: x.get('probability', 0), reverse=True)[:top_n]
    if not sorted_res:
        return '<div style="text-align:center;color:#5B6B80;font-size:9pt;">No data</div>'

    s_w, s_h = 280, 210
    n = len(sorted_res)
    row_h = s_h / n
    label_w = 70
    max_bar_w = s_w - label_w - 40

    bars = []
    for i, r in enumerate(sorted_res):
        prob = r.get('probability', 0)
        bar_w = (prob / 100.0) * max_bar_w
        y = i * row_h + row_h * 0.22
        bar_h = row_h * 0.56
        disease_label = (r.get('disease', '') or '')[:12]
        bars.append(
            f'<text x="{label_w - 4}" y="{y + bar_h*0.75}" text-anchor="end" '
            f'font-size="7.5" fill="{MUTED}">{disease_label}</text>'
            f'<rect x="{label_w}" y="{y}" width="{bar_w:.1f}" height="{bar_h:.1f}" fill="{ACCENT_BLUE}" rx="1.5"/>'
            f'<text x="{label_w + bar_w + 4}" y="{y + bar_h*0.75}" font-size="7.5" fill="{MUTED}">{prob}%</text>'
        )

    return f"""
<div style="text-align:center;">
  <svg width="{width_px}" height="{height_px}" viewBox="0 0 {s_w} {s_h}" xmlns="http://www.w3.org/2000/svg" direction="ltr">
    {''.join(bars)}
  </svg>
</div>"""


def build_charts_section(results: list, counts: dict):
    """
    Convenience function returning both charts as HTML strings.

    Returns:
        tuple: (pie_html, bar_html)
    """
    return build_pie_chart(counts), build_bar_chart(results)