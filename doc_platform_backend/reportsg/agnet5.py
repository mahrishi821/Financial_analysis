# agent5.py
"""
Agent 5: Report Generator
-------------------------
Inputs:
  - summary_html: str (basic HTML supported by ReportLab Paragraph)
  - insights: dict (arbitrary JSON; rendered as sections, lists and tables)
  - charts: list[dict] (Agent4 chart configs: type, title, series, options, encodings...)
  - output_path: str (where to write the PDF)

Output:
  - str: output_path (the file that was written)

Dependencies:
  pip install reportlab matplotlib python-dateutil
"""

from __future__ import annotations
import os
import io
import math
import tempfile
from typing import Any, Dict, List, Tuple

# PDF building
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image,
    Table, TableStyle, ListFlowable, ListItem, PageBreak
)

# Basic HTML rendering support by ReportLab's Paragraph:
# <b>, <i>, <u>, <br/>, <font>, <sup>, <sub>, <para>, <a href>, bullet lists via ListFlowable.

# Charting
import matplotlib
matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from dateutil import parser as dt_parser


# ---------------------------
# Helpers for content blocks
# ---------------------------

def _styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="H1", parent=styles["Heading1"], spaceAfter=12))
    styles.add(ParagraphStyle(name="H2", parent=styles["Heading2"], spaceAfter=8))
    styles.add(ParagraphStyle(name="H3", parent=styles["Heading3"], spaceAfter=6))
    styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=9, leading=12))
    styles.add(ParagraphStyle(name="Mono", parent=styles["BodyText"], fontName="Courier", fontSize=9, leading=12))
    return styles


def _to_paragraph_safe_html(html: str) -> str:
    """
    ReportLab Paragraph handles a *subset* of HTML.
    This helper does a very light sanitation for common issues.
    """
    if not isinstance(html, str):
        return ""
    # Normalize line breaks
    html = html.replace("\n", "<br/>")
    return html


def _kv_table(data: Dict[str, Any]) -> Table:
    """
    Render a shallow dict as two-column table.
    """
    rows = [["Key", "Value"]]
    for k, v in data.items():
        rows.append([str(k), str(v)])
    tbl = Table(rows, colWidths=[5*cm, 10*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F3F4F6")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#111827")),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D1D5DB")),
    ]))
    return tbl


def _render_insights(insights: Dict[str, Any], styles) -> List[Any]:
    """
    Convert an arbitrary insights JSON into readable blocks:
      - dicts as tables
      - lists as bullets
      - primitives as paragraphs
    Top-level keys become H2 sections.
    """
    flow: List[Any] = []
    if not isinstance(insights, dict):
        flow.append(Paragraph("No insights available.", styles["BodyText"]))
        return flow

    for section, payload in insights.items():
        flow.append(Paragraph(str(section).replace("_", " ").title(), styles["H2"]))
        flow.extend(_render_value(payload, styles))
        flow.append(Spacer(1, 8))
    return flow


def _render_value(v: Any, styles) -> List[Any]:
    blocks: List[Any] = []
    if isinstance(v, dict):
        # If dict values are primitives -> key-value table
        # Otherwise recurse per key
        if all(not isinstance(val, (dict, list)) for val in v.values()):
            blocks.append(_kv_table(v))
        else:
            for k, val in v.items():
                blocks.append(Paragraph(str(k).replace("_", " ").title(), styles["H3"]))
                blocks.extend(_render_value(val, styles))
                blocks.append(Spacer(1, 4))
    elif isinstance(v, list):
        items = []
        for item in v:
            if isinstance(item, (dict, list)):
                # nest complex items as separate blocks
                sub = _render_value(item, styles)
                items.append(ListItem(FlowableGroup(sub), leftIndent=12))
            else:
                items.append(ListItem(Paragraph(str(item), styles["BodyText"]), leftIndent=12))
        blocks.append(ListFlowable(items, bulletType="bullet"))
    else:
        blocks.append(Paragraph(str(v), styles["BodyText"]))
    return blocks


class FlowableGroup:
    """
    Tiny helper to allow a group of flowables to be used as a ListItem content.
    """
    def __init__(self, flowables: List[Any]):
        self.flowables = flowables
    def wrap(self, aW, aH):
        # Not directly used by ReportLab (wrapped by ListItem), but keep for completeness
        return (aW, aH)
    def drawOn(self, canvas, x, y, _sW=0):
        pass  # not called directly


# ---------------------------
# Chart rendering (Matplotlib)
# ---------------------------

def _parse_x(x):
    # Try date, else return as-is for categorical/numeric
    if isinstance(x, (int, float)):
        return x
    if isinstance(x, str):
        try:
            return dt_parser.parse(x)
        except Exception:
            return x
    return x


def _categorical_x(series):
    return not all(isinstance(_parse_x(x), (float, int)) or hasattr(_parse_x(x), "toordinal") for x in series)


def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)
    return path


def _fig_ax(figsize=(8, 4.5)):
    fig = plt.figure(figsize=figsize, dpi=150)
    ax = fig.add_subplot(111)
    return fig, ax


def _save_chart(fig, image_dir: str, base_name: str) -> str:
    _ensure_dir(image_dir)
    path = os.path.join(image_dir, f"{base_name}.png")
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def _render_line_bar_area(cfg: Dict[str, Any], image_dir: str, idx: int) -> str:
    """
    Supports: line, bar, area, stacked_bar, stacked_area
    """
    chart_type = cfg["type"]
    series = cfg.get("series", [])
    title = cfg.get("title", chart_type.title())
    x_is_date = False

    # Prepare X across all series (assume aligned)
    # Each series: {'label':..., 'data': [(x, y), ...], 'color': '#HEX'}
    xs = [ _parse_x(pt[0]) for pt in series[0]["data"] ] if series and series[0].get("data") else []
    if xs and hasattr(xs[0], "toordinal"):
        x_is_date = True

    fig, ax = _fig_ax()

    if chart_type in ("line", "area", "stacked_area"):
        stacked = chart_type == "stacked_area"
        if stacked:
            # stack areas by accumulating
            stack_vals = None
            for s in series:
                ys = [pt[1] for pt in s["data"]]
                if stack_vals is None:
                    stack_vals = ys
                else:
                    stack_vals = [a + b for a, b in zip(stack_vals, ys)]
                ax.fill_between(xs, stack_vals, step=None, alpha=0.5, label=s.get("label"))
        else:
            for s in series:
                ys = [pt[1] for pt in s["data"]]
                if chart_type == "area":
                    ax.fill_between(xs, ys, alpha=0.35, label=s.get("label"))
                    ax.plot(xs, ys)
                else:
                    ax.plot(xs, ys, label=s.get("label"))

    elif chart_type in ("bar", "stacked_bar"):
        labels = [pt[0] for pt in series[0]["data"]]
        n = len(labels)
        m = len(series)
        ind = range(n)
        width = 0.8
        if chart_type == "stacked_bar":
            bottoms = [0.0] * n
            for s in series:
                ys = [pt[1] for pt in s["data"]]
                ax.bar(labels, ys, bottom=bottoms, label=s.get("label"))
                bottoms = [a + b for a, b in zip(bottoms, ys)]
        else:
            # grouped bars
            bar_w = width / max(1, m)
            for j, s in enumerate(series):
                ys = [pt[1] for pt in s["data"]]
                # shift by j
                x_positions = [i + (j - (m-1)/2)*bar_w for i in range(n)]
                ax.bar(x_positions, ys, width=bar_w, label=s.get("label"))
            # set tick labels at centers
            ax.set_xticks(list(range(n)))
            ax.set_xticklabels([str(l) for l in labels], rotation=45, ha="right")

    # Titles/axes
    ax.set_title(title)
    x_title = cfg.get("encodings", {}).get("x_title")
    y_title = cfg.get("encodings", {}).get("y_title")
    if x_title:
        ax.set_xlabel(x_title)
    if y_title:
        ax.set_ylabel(y_title)

    if x_is_date:
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
        fig.autofmt_xdate()

    if len(series) > 1:
        ax.legend()

    return _save_chart(fig, image_dir, f"chart_{idx}")


def _render_scatter(cfg: Dict[str, Any], image_dir: str, idx: int) -> str:
    series = cfg.get("series", [])
    title = cfg.get("title", "Scatter")
    fig, ax = _fig_ax()

    for s in series:
        xs = [_parse_x(pt[0]) for pt in s.get("data", [])]
        ys = [pt[1] for pt in s.get("data", [])]
        ax.scatter(xs, ys, label=s.get("label"))

    ax.set_title(title)
    enc = cfg.get("encodings", {})
    if enc.get("x_title"): ax.set_xlabel(enc["x_title"])
    if enc.get("y_title"): ax.set_ylabel(enc["y_title"])
    if len(series) > 1: ax.legend()

    # date x?
    if series and series[0].get("data"):
        x0 = _parse_x(series[0]["data"][0][0])
        if hasattr(x0, "toordinal"):
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
            fig.autofmt_xdate()

    return _save_chart(fig, image_dir, f"chart_{idx}")


def _render_pie_or_donut(cfg: Dict[str, Any], image_dir: str, idx: int) -> str:
    # Expect first series only for pie/donut
    series = cfg.get("series", [])
    title = cfg.get("title", "Pie")
    donut = cfg["type"] == "donut"

    if not series:
        # nothing to render
        fig, ax = _fig_ax()
        ax.text(0.5, 0.5, "No data", ha="center", va="center")
        return _save_chart(fig, image_dir, f"chart_{idx}")

    s = series[0]
    labels = [str(pt[0]) for pt in s.get("data", [])]
    vals = [pt[1] for pt in s.get("data", [])]

    fig, ax = _fig_ax()
    if donut:
        wedges, _ = ax.pie(vals, labels=labels, wedgeprops=dict(width=0.4))
    else:
        wedges, _ = ax.pie(vals, labels=labels, autopct="%1.1f%%")
    ax.set_title(title)
    return _save_chart(fig, image_dir, f"chart_{idx}")


def _render_histogram(cfg: Dict[str, Any], image_dir: str, idx: int) -> str:
    # Use first series
    series = cfg.get("series", [])
    title = cfg.get("title", "Histogram")
    fig, ax = _fig_ax()

    if series:
        vals = [pt[1] for pt in series[0].get("data", [])]
        ax.hist(vals, bins="auto")
    else:
        ax.text(0.5, 0.5, "No data", ha="center", va="center")

    enc = cfg.get("encodings", {})
    if enc.get("y_title"): ax.set_ylabel(enc["y_title"])
    if enc.get("x_title"): ax.set_xlabel(enc["x_title"])
    ax.set_title(title)
    return _save_chart(fig, image_dir, f"chart_{idx}")


def _render_box(cfg: Dict[str, Any], image_dir: str, idx: int) -> str:
    series = cfg.get("series", [])
    title = cfg.get("title", "Box Plot")
    fig, ax = _fig_ax()

    if series:
        # Expect each series to be a group
        data = [[pt[1] for pt in s.get("data", [])] for s in series]
        labels = [s.get("label", f"S{i+1}") for i, s in enumerate(series)]
        ax.boxplot(data, labels=labels)
    else:
        ax.text(0.5, 0.5, "No data", ha="center", va="center")

    ax.set_title(title)
    enc = cfg.get("encodings", {})
    if enc.get("y_title"): ax.set_ylabel(enc["y_title"])
    return _save_chart(fig, image_dir, f"chart_{idx}")


def _render_bubble(cfg: Dict[str, Any], image_dir: str, idx: int) -> str:
    # Expect a single series with tuples (x, y, size) OR Agent4 variant with extra field in 'series' meta
    # Our Agent4 emits: bubble via _build_bubble -> each series has data [(x, y, size)]
    series = cfg.get("series", [])
    title = cfg.get("title", "Bubble Chart")
    fig, ax = _fig_ax()

    for s in series:
        xs = []
        ys = []
        sizes = []
        for pt in s.get("data", []):
            if len(pt) >= 3:
                xs.append(_parse_x(pt[0]))
                ys.append(pt[1])
                sizes.append(pt[2])
        # scale sizes
        if sizes:
            # Normalize to a reasonable dot size range
            mn, mx = min(sizes), max(sizes)
            rng = (mx - mn) or 1.0
            scaled = [50 + 250 * (v - mn) / rng for v in sizes]
        else:
            scaled = 80
        ax.scatter(xs, ys, s=scaled, alpha=0.6, label=s.get("label"))

    ax.set_title(title)
    enc = cfg.get("encodings", {})
    if enc.get("x_title"): ax.set_xlabel(enc["x_title"])
    if enc.get("y_title"): ax.set_ylabel(enc["y_title"])
    if len(series) > 1: ax.legend()

    # date x?
    if series and series[0].get("data"):
        x0 = _parse_x(series[0]["data"][0][0])
        if hasattr(x0, "toordinal"):
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
            fig.autofmt_xdate()

    return _save_chart(fig, image_dir, f"chart_{idx}")


def _render_chart_to_image(cfg: Dict[str, Any], image_dir: str, idx: int) -> str:
    t = (cfg.get("type") or "").lower()
    if t in ("line", "bar", "area", "stacked_bar", "stacked_area"):
        return _render_line_bar_area(cfg, image_dir, idx)
    elif t == "scatter":
        return _render_scatter(cfg, image_dir, idx)
    elif t in ("pie", "donut"):
        return _render_pie_or_donut(cfg, image_dir, idx)
    elif t == "histogram":
        return _render_histogram(cfg, image_dir, idx)
    elif t == "box":
        return _render_box(cfg, image_dir, idx)
    elif t == "bubble":
        return _render_bubble(cfg, image_dir, idx)
    else:
        # Unknown -> simple text image
        fig, ax = _fig_ax()
        ax.text(0.5, 0.5, f"Unsupported chart type: {t}", ha="center", va="center")
        return _save_chart(fig, image_dir, f"chart_{idx}")


# ---------------------------
# PDF generation
# ---------------------------

def _header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.HexColor("#6B7280"))
    canvas.drawRightString(w - 1.5*cm, 1.0*cm, f"Page {doc.page}")
    canvas.restoreState()


def generate_pdf_report(
    summary_html: str,
    insights: Dict[str, Any],
    charts: List[Dict[str, Any]],
    output_path: str,
    title: str = "Financial Analysis Report",
    author: str = "Agent 5",
) -> str:
    """
    Build the PDF in the fixed order:
      1) Summary
      2) Insights
      3) Charts
    Returns `output_path`.
    """
    print(f"Generating PDF for {title}")
    styles = _styles()
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=2*cm,
        rightMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
        title=title,
        author=author,
    )

    story: List[Any] = []

    # Title
    story.append(Paragraph(title, styles["H1"]))
    story.append(Paragraph(f"Author: {author}", styles["Small"]))
    story.append(Spacer(1, 12))

    # 1) Summary
    story.append(Paragraph("Summary", styles["H2"]))
    story.append(Paragraph(_to_paragraph_safe_html(summary_html or "—"), styles["BodyText"]))
    story.append(Spacer(1, 12))

    # 2) Insights
    story.append(Paragraph("Insights", styles["H2"]))
    story.extend(_render_insights(insights or {}, styles))
    story.append(Spacer(1, 12))

    # 3) Charts
    story.append(Paragraph("Visualizations", styles["H2"]))

    # Render all charts to temporary images, then embed
    img_dir = tempfile.mkdtemp(prefix="agent5_charts_")
    for i, cfg in enumerate(charts or [], start=1):
        img_path = _render_chart_to_image(cfg, img_dir, i)
        # Title above each chart
        story.append(Paragraph(cfg.get("title", cfg.get("type", "Chart")).strip(), styles["H3"]))
        im = Image(img_path, width=16*cm, height=9*cm)  # 16:9 card
        story.append(im)
        # Optional: small metrics section if available
        metrics = cfg.get("metrics")
        if isinstance(metrics, dict) and metrics:
            story.append(Spacer(1, 4))
            story.append(Paragraph("Metrics", styles["Small"]))
            # Flatten metrics dict to a small key-value table
            flat = {}
            for k, v in metrics.items():
                if isinstance(v, dict):
                    for kk, vv in v.items():
                        flat[f"{k} — {kk}"] = vv
                else:
                    flat[k] = v
            story.append(_kv_table(flat))
        story.append(Spacer(1, 12))

    # Build
    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    print(f"Wrote to {output_path}")
    return output_path


# ---------------------------
# Example usage (manual test)
# ---------------------------
# if __name__ == "__main__":
#     # Minimal smoke test:
#     example_summary = "<b>Executive Summary:</b> Cash flows stabilized; balances amortize monthly."
#     example_insights = {
#         "kpis": {"IRR": "9.63%", "Total Interest": 37644292.24, "Principal Paid": 200000000},
#         "trends": ["Interest declining with balance", "Regular principal amortization"],
#         "notes": ["All figures in native currency", "Dates normalized to month-end"]
#     }
#     example_chart = {
#         "type": "line",
#         "title": "Sample Line",
#         "encodings": {"x_title": "Date", "y_title": "Value"},
#         "series": [
#             {"label": "A", "data": [("2024-01-31", 1), ("2024-02-29", 2), ("2024-03-31", 3)]},
#             {"label": "B", "data": [("2024-01-31", 2), ("2024-02-29", 1), ("2024-03-31", 4)]},
#         ],
#     }
#     out = generate_pdf_report(example_summary, example_insights, [example_chart], "agent5_demo.pdf")
#     print("Wrote:", out)
