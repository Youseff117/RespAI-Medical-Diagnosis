"""
Vector Icons for PDF Report
============================
"""

from reportlab.graphics.shapes import (
    Drawing, Rect, Line, Circle, Polygon
)
from .config import (
    PRIMARY_BLUE, SOFT_BLUE,
    STATUS_BG, STATUS_ACCENT
)
from reportlab.lib import colors


def vector_icon(name, size=0.5, color=None, unit='cm'):
    """Return a vector icon as a ReportLab Drawing object."""
    if color is None:
        color = PRIMARY_BLUE
    
    d = Drawing(size, size)
    s = size
    
    if name == "summary":
        d.add(Rect(0, 0, s, s, fillColor=SOFT_BLUE, strokeColor=color, strokeWidth=0.5, rx=2, ry=2))
        d.add(Rect(s * 0.2, s * 0.55, s * 0.6, s * 0.12, fillColor=color, strokeColor=None))
        d.add(Rect(s * 0.2, s * 0.32, s * 0.45, s * 0.12, fillColor=color, strokeColor=None))
        d.add(Rect(s * 0.2, s * 0.1, s * 0.55, s * 0.12, fillColor=color, strokeColor=None))
    
    elif name == "patient":
        d.add(Circle(s / 2, s / 2, s * 0.45, fillColor=SOFT_BLUE, strokeColor=color, strokeWidth=0.5))
        d.add(Circle(s / 2, s * 0.38, s * 0.14, fillColor=color, strokeColor=None))
        d.add(Rect(s * 0.28, s * 0.55, s * 0.44, s * 0.22, fillColor=color, strokeColor=None, rx=2, ry=2))
    
    elif name == "findings":
        d.add(Circle(s / 2, s / 2, s * 0.45, fillColor=SOFT_BLUE, strokeColor=color, strokeWidth=0.5))
        d.add(Line(s * 0.2, s * 0.5, s * 0.8, s * 0.5, strokeColor=color, strokeWidth=1.2))
        d.add(Line(s * 0.5, s * 0.2, s * 0.5, s * 0.8, strokeColor=color, strokeWidth=1.2))
    
    elif name == "ai":
        d.add(Rect(s * 0.1, s * 0.15, s * 0.8, s * 0.7, fillColor=SOFT_BLUE, strokeColor=color, strokeWidth=0.5, rx=3, ry=3))
        d.add(Circle(s * 0.35, s * 0.5, s * 0.07, fillColor=color, strokeColor=None))
        d.add(Circle(s * 0.65, s * 0.5, s * 0.07, fillColor=color, strokeColor=None))
        d.add(Line(s * 0.3, s * 0.3, s * 0.7, s * 0.3, strokeColor=color, strokeWidth=1))
    
    elif name == "recommend":
        d.add(Rect(s * 0.15, s * 0.05, s * 0.7, s * 0.9, fillColor=SOFT_BLUE, strokeColor=color, strokeWidth=0.5, rx=2, ry=2))
        d.add(Line(s * 0.28, s * 0.7, s * 0.72, s * 0.7, strokeColor=color, strokeWidth=0.8))
        d.add(Line(s * 0.28, s * 0.5, s * 0.72, s * 0.5, strokeColor=color, strokeWidth=0.8))
        d.add(Line(s * 0.28, s * 0.3, s * 0.6, s * 0.3, strokeColor=color, strokeWidth=0.8))
    
    elif name == "warning":
        d.add(Polygon([s * 0.5, s * 0.05, s * 0.95, s * 0.9, s * 0.05, s * 0.9],
                      fillColor=colors.HexColor('#FFF1E6'),
                      strokeColor=colors.HexColor('#D97706'), strokeWidth=0.8))
        d.add(Line(s * 0.5, s * 0.35, s * 0.5, s * 0.65,
                   strokeColor=colors.HexColor('#D97706'), strokeWidth=1.5))
        d.add(Circle(s * 0.5, s * 0.78, s * 0.05,
                     fillColor=colors.HexColor('#D97706'), strokeColor=None))
    
    elif name == "doctor":
        d.add(Circle(s / 2, s * 0.32, s * 0.22, fillColor=SOFT_BLUE, strokeColor=color, strokeWidth=0.5))
        d.add(Rect(s * 0.18, s * 0.55, s * 0.64, s * 0.4, fillColor=SOFT_BLUE, strokeColor=color, strokeWidth=0.5, rx=2, ry=2))
        d.add(Line(s * 0.5, s * 0.6, s * 0.5, s * 0.85, strokeColor=color, strokeWidth=1))
        d.add(Line(s * 0.38, s * 0.72, s * 0.62, s * 0.72, strokeColor=color, strokeWidth=1))
    
    elif name == "chart":
        d.add(Rect(0, 0, s, s, fillColor=SOFT_BLUE, strokeColor=color, strokeWidth=0.5, rx=2, ry=2))
        d.add(Rect(s * 0.15, s * 0.5, s * 0.15, s * 0.35, fillColor=color, strokeColor=None))
        d.add(Rect(s * 0.4, s * 0.25, s * 0.15, s * 0.6, fillColor=color, strokeColor=None))
        d.add(Rect(s * 0.65, s * 0.38, s * 0.15, s * 0.47, fillColor=color, strokeColor=None))
    
    elif name == "tech":
        d.add(Rect(s * 0.1, s * 0.1, s * 0.8, s * 0.8, fillColor=SOFT_BLUE, strokeColor=color, strokeWidth=0.5, rx=2, ry=2))
        d.add(Circle(s * 0.5, s * 0.5, s * 0.2, fillColor=None, strokeColor=color, strokeWidth=0.8))
        d.add(Circle(s * 0.5, s * 0.5, s * 0.07, fillColor=color, strokeColor=None))
    
    elif name == "stats":
        d.add(Rect(0, 0, s, s, fillColor=SOFT_BLUE, strokeColor=color, strokeWidth=0.5, rx=2, ry=2))
        d.add(Line(s * 0.15, s * 0.85, s * 0.15, s * 0.15, strokeColor=color, strokeWidth=1))
        d.add(Line(s * 0.15, s * 0.15, s * 0.85, s * 0.15, strokeColor=color, strokeWidth=1))
        d.add(Rect(s * 0.25, s * 0.55, s * 0.12, s * 0.28, fillColor=color, strokeColor=None))
        d.add(Rect(s * 0.45, s * 0.35, s * 0.12, s * 0.48, fillColor=color, strokeColor=None))
        d.add(Rect(s * 0.65, s * 0.45, s * 0.12, s * 0.38, fillColor=color, strokeColor=None))
    
    elif name == "shield":
        d.add(Polygon([s * 0.5, s * 0.05, s * 0.9, s * 0.25, s * 0.9, s * 0.6,
                       s * 0.5, s * 0.95, s * 0.1, s * 0.6, s * 0.1, s * 0.25],
                      fillColor=SOFT_BLUE, strokeColor=color, strokeWidth=0.8))
        d.add(Line(s * 0.35, s * 0.55, s * 0.48, s * 0.68, strokeColor=color, strokeWidth=1.5))
        d.add(Line(s * 0.48, s * 0.68, s * 0.68, s * 0.42, strokeColor=color, strokeWidth=1.5))
    
    elif name == "book":
        d.add(Rect(s * 0.1, s * 0.1, s * 0.8, s * 0.8, fillColor=SOFT_BLUE, strokeColor=color, strokeWidth=0.5, rx=1, ry=1))
        d.add(Line(s * 0.5, s * 0.15, s * 0.5, s * 0.85, strokeColor=color, strokeWidth=0.8))
        d.add(Line(s * 0.15, s * 0.35, s * 0.45, s * 0.35, strokeColor=color, strokeWidth=0.5))
        d.add(Line(s * 0.15, s * 0.5, s * 0.45, s * 0.5, strokeColor=color, strokeWidth=0.5))
        d.add(Line(s * 0.15, s * 0.65, s * 0.45, s * 0.65, strokeColor=color, strokeWidth=0.5))
    
    elif name == "normal":
        d.add(Circle(s / 2, s / 2, s * 0.45, fillColor=STATUS_BG['green'],
                     strokeColor=STATUS_ACCENT['green'], strokeWidth=1))
        d.add(Line(s * 0.3, s * 0.5, s * 0.45, s * 0.65,
                   strokeColor=STATUS_ACCENT['green'], strokeWidth=1.5))
        d.add(Line(s * 0.45, s * 0.65, s * 0.7, s * 0.38,
                   strokeColor=STATUS_ACCENT['green'], strokeWidth=1.5))
    
    elif name == "hospital":
        d.add(Rect(s * 0.1, s * 0.2, s * 0.8, s * 0.7, fillColor=SOFT_BLUE, strokeColor=color, strokeWidth=0.5, rx=2, ry=2))
        d.add(Line(s * 0.5, s * 0.35, s * 0.5, s * 0.75, strokeColor=color, strokeWidth=1.5))
        d.add(Line(s * 0.3, s * 0.55, s * 0.7, s * 0.55, strokeColor=color, strokeWidth=1.5))
        d.add(Rect(s * 0.35, s * 0.05, s * 0.3, s * 0.15, fillColor=SOFT_BLUE, strokeColor=color, strokeWidth=0.5))
    
    elif name == "quality":
        d.add(Rect(0, 0, s, s, fillColor=SOFT_BLUE, strokeColor=color, strokeWidth=0.5, rx=2, ry=2))
        d.add(Circle(s * 0.5, s * 0.5, s * 0.3, fillColor=None, strokeColor=color, strokeWidth=0.8))
        d.add(Circle(s * 0.5, s * 0.5, s * 0.12, fillColor=color, strokeColor=None))
    
    elif name == "confidence":
        d.add(Rect(0, 0, s, s, fillColor=SOFT_BLUE, strokeColor=color, strokeWidth=0.5, rx=2, ry=2))
        d.add(Polygon([s * 0.5, s * 0.15, s * 0.85, s * 0.5,
                       s * 0.5, s * 0.85, s * 0.15, s * 0.5],
                      fillColor=None, strokeColor=color, strokeWidth=0.8))
        d.add(Circle(s * 0.5, s * 0.5, s * 0.08, fillColor=color, strokeColor=None))
    
    elif name == "heatmap":
        d.add(Rect(0, 0, s, s, fillColor=SOFT_BLUE, strokeColor=color, strokeWidth=0.5, rx=2, ry=2))
        cell = s / 3
        hm_colors = [
            colors.HexColor('#4CAF50'), colors.HexColor('#FFEB3B'), colors.HexColor('#FF9800'),
            colors.HexColor('#FFEB3B'), colors.HexColor('#F44336'), colors.HexColor('#FF9800'),
            colors.HexColor('#4CAF50'), colors.HexColor('#FF9800'), colors.HexColor('#FFEB3B'),
        ]
        for row in range(3):
            for col in range(3):
                d.add(Rect(col * cell + s * 0.05, row * cell + s * 0.05,
                           cell - s * 0.02, cell - s * 0.02,
                           fillColor=hm_colors[row * 3 + col], strokeColor=None))
    
    elif name == "compare":
        d.add(Rect(s * 0.05, s * 0.15, s * 0.4, s * 0.7, fillColor=SOFT_BLUE, strokeColor=color, strokeWidth=0.5, rx=2, ry=2))
        d.add(Rect(s * 0.55, s * 0.15, s * 0.4, s * 0.7, fillColor=SOFT_BLUE, strokeColor=color, strokeWidth=0.5, rx=2, ry=2))
        d.add(Line(s * 0.5, s * 0.3, s * 0.5, s * 0.7, strokeColor=color, strokeWidth=0.5))
    
    elif name == "severity":
        d.add(Rect(0, 0, s, s, fillColor=SOFT_BLUE, strokeColor=color, strokeWidth=0.5, rx=2, ry=2))
        bars = [('green', 0.7), ('yellow', 0.5), ('orange', 0.3), ('red', 0.1)]
        for clr, y in bars:
            d.add(Rect(s * 0.15, s * y, s * 0.7, s * 0.1,
                       fillColor=STATUS_ACCENT[clr], strokeColor=None))
    
    elif name == "timeline":
        d.add(Line(s * 0.1, s * 0.5, s * 0.9, s * 0.5, strokeColor=color, strokeWidth=1))
        for cx in (0.2, 0.5, 0.8):
            d.add(Circle(s * cx, s * 0.5, s * 0.08, fillColor=color, strokeColor=None))
    
    elif name == "pipeline":
        for bx in (0.05, 0.4, 0.75):
            d.add(Rect(s * bx, s * 0.3, s * 0.2, s * 0.4,
                       fillColor=SOFT_BLUE, strokeColor=color, strokeWidth=0.5))
        d.add(Line(s * 0.25, s * 0.5, s * 0.4, s * 0.5, strokeColor=color, strokeWidth=1))
        d.add(Line(s * 0.6, s * 0.5, s * 0.75, s * 0.5, strokeColor=color, strokeWidth=1))
    
    else:
        d.add(Circle(s / 2, s / 2, s * 0.4, fillColor=SOFT_BLUE, strokeColor=color, strokeWidth=0.5))
    
    return d