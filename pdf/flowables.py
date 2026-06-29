"""
Custom Flowables for PDF Report
================================
Contains custom drawing elements used in the report:
- GradientProgressBar
- RiskGauge
- StarRating
"""

import math
from reportlab.platypus import Flowable
from reportlab.graphics.shapes import Drawing, Rect, Line, Circle, Polygon, Wedge
from reportlab.graphics import renderPDF
from reportlab.lib import colors

from .config import ACCENT_BLUE, STATUS_ACCENT, INK, WHITE, MUTED
from .styles import FONT_BOLD, FONT_REGULAR


class GradientProgressBar(Flowable):
    """Simple progress bar - NO text inside, NO 30 steps."""
    def __init__(self, width, height, percentage, color_key='green'):
        super().__init__()
        self.width = width
        self.height = height
        self.percentage = max(0.0, min(100.0, float(percentage)))
        self.color_key = color_key

    def draw(self):
        c = self.canv
        w, h = self.width, self.height
        
        # 1. Background track
        c.setFillColor(colors.HexColor('#EEF2F7'))
        c.roundRect(0, 0, w, h, 3, fill=1, stroke=0)
        
        # 2. Filled portion
        fill_w = (self.percentage / 100.0) * w
        if fill_w > 1:
            accent = STATUS_ACCENT.get(self.color_key, ACCENT_BLUE)
            c.setFillColor(accent)
            c.roundRect(0, 0, fill_w, h, 3, fill=1, stroke=0)


class RiskGauge(Flowable):
    """Circular gauge showing overall risk level."""
    def __init__(self, size, percentage, color, label):
        super().__init__()
        self.size = size
        self.width = size
        self.height = size
        self.percentage = max(0.0, min(100.0, float(percentage)))
        self.color = color
        self.label = label

    def draw(self):
        c = self.canv
        cx, cy = self.size / 2, self.size / 2
        r_outer = self.size * 0.42
        r_inner = r_outer * 0.65
        stroke_w = r_outer - r_inner

        # Background arc
        c.setStrokeColor(colors.HexColor('#E5E7EB'))
        c.setLineWidth(stroke_w)
        c.arc(cx - r_outer + stroke_w / 2, cy - r_outer + stroke_w / 2,
              cx + r_outer - stroke_w / 2, cy + r_outer - stroke_w / 2,
              startAng=-45, extent=270)

        # Value arc
        if self.percentage > 0:
            angle = (self.percentage / 100.0) * 270
            c.setStrokeColor(self.color)
            c.arc(cx - r_outer + stroke_w / 2, cy - r_outer + stroke_w / 2,
                  cx + r_outer - stroke_w / 2, cy + r_outer - stroke_w / 2,
                  startAng=225, extent=angle)

        # White inner circle
        c.setFillColor(WHITE)
        c.circle(cx, cy, r_inner - stroke_w * 0.1, fill=1, stroke=0)

        # Percentage text
        c.setFont(FONT_BOLD, max(8, int(self.size * 0.17)))
        c.setFillColor(self.color)
        c.drawCentredString(cx, cy + self.size * 0.04, f"{int(self.percentage)}%")

        # Label text
        c.setFont(FONT_REGULAR, max(6, int(self.size * 0.09)))
        c.setFillColor(MUTED)
        c.drawCentredString(cx, cy - self.size * 0.15, self.label)


class StarRating(Flowable):
    """5-star visual rating."""
    def __init__(self, score, max_score=100, size=0.6):
        super().__init__()
        self.score = score
        self.max_score = max_score
        self.size = size
        self.width = size * 5.8
        self.height = size * 1.1

    def _star_points(self, cx, cy, r_out, r_in, n=5):
        pts = []
        for i in range(n * 2):
            angle = math.pi / 2 + i * math.pi / n
            r = r_out if i % 2 == 0 else r_in
            pts.extend([cx + r * math.cos(angle), cy + r * math.sin(angle)])
        return pts

    def draw(self):
        c = self.canv
        stars_full = (self.score / self.max_score) * 5
        s = self.size
        for i in range(5):
            cx = i * s * 1.1 + s * 0.5
            cy = s * 0.5
            if i + 1 <= stars_full:
                fill = colors.HexColor('#F59E0B')
            elif i + 0.5 <= stars_full:
                fill = colors.HexColor('#FCD34D')
            else:
                fill = colors.HexColor('#D1D5DB')
            pts = self._star_points(cx, cy, s * 0.48, s * 0.2)
            p = c.beginPath()
            p.moveTo(pts[0], pts[1])
            for j in range(2, len(pts), 2):
                p.lineTo(pts[j], pts[j + 1])
            p.close()
            c.setFillColor(fill)
            c.setStrokeColor(colors.HexColor('#E5E7EB'))
            c.setLineWidth(0.3)
            c.drawPath(p, fill=1, stroke=1)