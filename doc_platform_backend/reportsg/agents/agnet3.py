# app/agents/report_generator_agent.py

import os, tempfile, math
from typing import Any, Dict, List
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image,
    Table, TableStyle, ListFlowable, ListItem
)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from dateutil import parser as dt_parser


class ReportGeneratorAgent:
    """
    Agent 5:
    Builds a financial analysis PDF report with:
      - Executive summary
      - Insights (tables, lists, metrics)
      - Visualizations (charts from Agent4)
    """

    def __init__(self, title: str = "Financial Analysis Report", author: str = "Agent 5"):
        self.title = title
        self.author = author
        self.styles = self._init_styles()

    # ---------------- Styles ----------------
    def _init_styles(self):
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="H1", parent=styles["Heading1"], spaceAfter=12))
        styles.add(ParagraphStyle(name="H2", parent=styles["Heading2"], spaceAfter=8))
        styles.add(ParagraphStyle(name="H3", parent=styles["Heading3"], spaceAfter=6))
        styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=9, leading=12))
        return styles

    # ---------------- Helpers ----------------
    def _to_paragraph_safe_html(self, html: str) -> str:
        return (html or "").replace("\n", "<br/>")

    def _kv_table(self, data: Dict[str, Any]) -> Table:
        rows = [["Key", "Value"]] + [[str(k), str(v)] for k, v in data.items()]
        tbl = Table(rows, colWidths=[5*cm, 10*cm])
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F3F4F6")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D1D5DB")),
        ]))
        return tbl

    def _render_insights(self, insights: Dict[str, Any]) -> List[Any]:
        flow = []
        if not isinstance(insights, dict):
            return [Paragraph("No insights available.", self.styles["BodyText"])]

        for section, payload in insights.items():
            flow.append(Paragraph(str(section).title(), self.styles["H2"]))
            flow.extend(self._render_value(payload))
            flow.append(Spacer(1, 8))
        return flow

    def _render_value(self, v: Any) -> List[Any]:
        if isinstance(v, dict):
            if all(not isinstance(val, (dict, list)) for val in v.values()):
                return [self._kv_table(v)]
            out = []
            for k, val in v.items():
                out.append(Paragraph(str(k).title(), self.styles["H3"]))
                out.extend(self._render_value(val))
            return out
        elif isinstance(v, list):
            items = [ListItem(Paragraph(str(item), self.styles["BodyText"]), leftIndent=12) for item in v]
            return [ListFlowable(items, bulletType="bullet")]
        else:
            return [Paragraph(str(v), self.styles["BodyText"])]

    # ---------------- Chart Rendering ----------------
    def _parse_x(self, x):
        try:
            return dt_parser.parse(x) if isinstance(x, str) else x
        except Exception:
            return x

    def _fig_ax(self, figsize=(8, 4.5)):
        fig = plt.figure(figsize=figsize, dpi=150)
        return fig, fig.add_subplot(111)

    def _save_chart(self, fig, img_dir: str, name: str):
        os.makedirs(img_dir, exist_ok=True)
        path = os.path.join(img_dir, f"{name}.png")
        fig.tight_layout()
        fig.savefig(path, bbox_inches="tight")
        plt.close(fig)
        return path

    def _render_chart(self, cfg: Dict[str, Any], img_dir: str, idx: int) -> str:
        t = (cfg.get("type") or "").lower()
        title = cfg.get("title", t.title())
        fig, ax = self._fig_ax()

        if t == "line":
            for s in cfg.get("series", []):
                xs = [self._parse_x(p[0]) for p in s.get("data", [])]
                ys = [p[1] for p in s.get("data", [])]
                ax.plot(xs, ys, label=s.get("label"))
        elif t == "bar":
            for s in cfg.get("series", []):
                xs = [p[0] for p in s.get("data", [])]
                ys = [p[1] for p in s.get("data", [])]
                ax.bar(xs, ys, label=s.get("label"))
        elif t == "pie":
            s = cfg.get("series", [{}])[0]
            labels = [str(p[0]) for p in s.get("data", [])]
            vals = [p[1] for p in s.get("data", [])]
            ax.pie(vals, labels=labels, autopct="%1.1f%%")
        else:
            ax.text(0.5, 0.5, f"Unsupported: {t}", ha="center", va="center")

        ax.set_title(title)
        if len(cfg.get("series", [])) > 1:
            ax.legend()
        return self._save_chart(fig, img_dir, f"chart_{idx}")

    # ---------------- PDF Generation ----------------
    def _header_footer(self, canvas, doc):
        w, h = A4
        canvas.setFont("Helvetica", 9)
        canvas.setFillColor(colors.HexColor("#6B7280"))
        canvas.drawRightString(w - 1.5*cm, 1.0*cm, f"Page {doc.page}")

    def generate_report(self, summary_html: str, insights: Dict[str, Any], charts: List[Dict[str, Any]], output_path: str) -> str:
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            leftMargin=2*cm, rightMargin=2*cm,
            topMargin=2*cm, bottomMargin=2*cm,
            title=self.title, author=self.author
        )
        story: List[Any] = []

        # Title
        story.append(Paragraph(self.title, self.styles["H1"]))
        story.append(Paragraph(f"Author: {self.author}", self.styles["Small"]))
        story.append(Spacer(1, 12))

        # Summary
        story.append(Paragraph("Summary", self.styles["H2"]))
        story.append(Paragraph(self._to_paragraph_safe_html(summary_html or "—"), self.styles["BodyText"]))
        story.append(Spacer(1, 12))

        # Insights
        story.append(Paragraph("Insights", self.styles["H2"]))
        story.extend(self._render_insights(insights))
        story.append(Spacer(1, 12))

        # Charts
        story.append(Paragraph("Visualizations", self.styles["H2"]))
        img_dir = tempfile.mkdtemp(prefix="agent5_charts_")
        for i, cfg in enumerate(charts or [], 1):
            img_path = self._render_chart(cfg, img_dir, i)
            story.append(Paragraph(cfg.get("title", "Chart"), self.styles["H3"]))
            story.append(Image(img_path, width=16*cm, height=9*cm))
            story.append(Spacer(1, 12))

        doc.build(story, onFirstPage=self._header_footer, onLaterPages=self._header_footer)
        return output_path
