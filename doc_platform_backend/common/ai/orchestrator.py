# common/ai/orchestrator.py
import json
from common.ai.agents.data_analyst import DataAnalyst
from common.ai.agents.viz_agent import VizAgent
from common.ai.agents.insights_agent import InsightsAgent
from common.ai.agents.writer import Writer

class FinanceReportOrchestrator:
    """
    Orchestrates the full agentic pipeline from extracted_text.
    """
    def __init__(self, model="openai/gpt-4o-mini"):
        self.analyst = DataAnalyst()
        self.viz = VizAgent()
        self.insights = InsightsAgent(model=model)
        self.writer = Writer()

    def _truncate(self, text, limit=4000):
        return (text[:limit] + " ... [truncated]") if text and len(text) > limit else text

    def run(self, file_name, file_type, extracted_text: str):
        # 1) Analyze data & compute KPIs
        analysis = self.analyst.analyze(extracted_text)
        kpis = analysis["kpis"]
        best_for_plot = analysis["best_for_plot"]

        # 2) Generate charts
        charts = []
        if best_for_plot:
            sheet_name, num_df = best_for_plot
            ts = self.viz.plot_timeseries(sheet_name, num_df)
            if ts:
                charts.append((f"{sheet_name} — Trend", ts))
            bars = self.viz.plot_bar_totals(sheet_name, num_df)
            if bars:
                charts.append((f"{sheet_name} — Column Totals", bars))

        # 3) Insights (strictly from KPIs JSON)
        insights_html = self.insights.generate_html_insights(kpis, sheet_hint=(best_for_plot[0] if best_for_plot else None))

        # 4) KPI table HTML
        kpi_html = self.writer.table_html_from_kpis(kpis)

        # 5) Compose final HTML
        html = self.writer.compose_html(
            file_name=file_name,
            file_type=file_type,
            insights_html=insights_html,
            kpi_html=kpi_html,
            charts_base64=charts,
            raw_excerpt=self._truncate(extracted_text, 10000)
        )
        return html
