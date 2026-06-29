"""
Chart Builders for PDF Report
==============================

This module contains functions to build chart drawings:
- build_pie_chart(): Risk distribution pie chart
- build_bar_chart(): Disease probability horizontal bar chart

Dependencies:
- config.py (for colors)
- styles.py (for fonts)
"""

from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import HorizontalBarChart

from .config import (
    STATUS_ACCENT, ACCENT_BLUE, MUTED, WHITE,
)
from .styles import FONT_REGULAR, FONT_SEMIBOLD, PRIMARY_BLUE


def build_pie_chart(counts: dict, width: float = 7.0, height: float = 5.0) -> Drawing:
    """
    Build a pie chart showing risk distribution.
    
    Args:
        counts: Dict with keys 'green', 'yellow', 'orange', 'red' and count values
        width: Chart width in cm (default: 7.0)
        height: Chart height in cm (default: 5.0)
    
    Returns:
        Drawing: ReportLab Drawing object containing the pie chart.
    """
    pie_d = Drawing(width, height)
    
    pie = Pie()
    pie.x = 1.5
    pie.y = 0.5
    pie.width = 4.0
    pie.height = 4.0
    
    # Use max(0.01) to avoid zero-slice errors
    pie.data = [
        max(counts.get('green', 0), 0.01),
        max(counts.get('yellow', 0), 0.01),
        max(counts.get('orange', 0), 0.01),
        max(counts.get('red', 0), 0.01),
    ]
    pie.labels = ['Normal', 'Low', 'Moderate', 'High']
    
    # Styling
    pie.slices.strokeWidth = 0.8
    pie.slices.strokeColor = WHITE
    pie.slices[0].fillColor = STATUS_ACCENT['green']
    pie.slices[1].fillColor = STATUS_ACCENT['yellow']
    pie.slices[2].fillColor = STATUS_ACCENT['orange']
    pie.slices[3].fillColor = STATUS_ACCENT['red']
    
    # Labels outside the pie
    pie.slices.labelRadius = 1.25
    pie.slices.fontName = FONT_REGULAR
    pie.slices.fontSize = 7
    
    pie_d.add(pie)
    return pie_d


def build_bar_chart(results: list, top_n: int = 8, width: float = 9.0, height: float = 5.0) -> Drawing:
    """
    Build a horizontal bar chart showing disease probabilities.
    
    Args:
        results: List of result dicts (must have 'disease' and 'probability' keys)
        top_n: Number of top diseases to show (default: 8)
        width: Chart width in cm (default: 9.0)
        height: Chart height in cm (default: 5.0)
    
    Returns:
        Drawing: ReportLab Drawing object containing the bar chart.
    """
    # Sort by probability descending and take top N
    sorted_res = sorted(results, key=lambda x: x.get('probability', 0), reverse=True)[:top_n]
    
    bar_d = Drawing(width, height)
    
    bc = HorizontalBarChart()
    bc.x = 3.0
    bc.y = 0.4
    bc.height = 4.2
    bc.width = 5.5
    
    # Data
    bc.data = [[r.get('probability', 0) for r in sorted_res]]
    bc.categoryAxis.categoryNames = [r.get('disease', '')[:10] for r in sorted_res]
    
    # Category axis (disease names) styling
    bc.categoryAxis.labels.fontName = FONT_REGULAR
    bc.categoryAxis.labels.fontSize = 7
    bc.categoryAxis.labels.fillColor = MUTED
    bc.categoryAxis.labels.dx = -5
    
    # Value axis (probability) styling
    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = 100
    bc.valueAxis.valueStep = 25
    bc.valueAxis.labels.fontName = FONT_REGULAR
    bc.valueAxis.labels.fontSize = 7
    bc.valueAxis.labels.fillColor = MUTED
    
    # Bar styling
    bc.bars[0].fillColor = ACCENT_BLUE
    bc.bars[0].strokeColor = None
    bc.barWidth = 0.38
    bc.groupSpacing = 0.1
    
    bar_d.add(bc)
    return bar_d


def build_charts_section(results: list, counts: dict):
    """
    Build the complete charts section with both pie and bar charts.
    
    This is a convenience function that returns both charts together.
    
    Args:
        results: List of result dicts
        counts: Dict with color counts
    
    Returns:
        tuple: (pie_drawing, bar_drawing)
    """
    pie = build_pie_chart(counts)
    bar = build_bar_chart(results)
    return pie, bar