# common/ai/agents/insights_agent.py
import json
from common.ai.openrouter_client import openrouter_chat

INSIGHTS_SYSTEM = (
    "You are a senior financial analyst. "
    "You MUST ONLY use the facts provided in the input JSON/tables. "
    "Do NOT invent numbers or outside facts. "
    "Write concise, decision-ready insights in HTML with headings and bullet points. "
    "If numbers are needed, reuse exactly what’s provided. "
)

class InsightsAgent:
    def __init__(self, model="openai/gpt-4o-mini"):
        self.model = model

    def generate_html_insights(self, kpi_snapshot: dict, sheet_hint=None):
        """
        kpi_snapshot: dict like {"Sheet1": {"Revenue": {...}, "Cost": {...}}, ...}
        """
        user_prompt = (
            "Generate an HTML 'Executive Summary' and 'Key Insights' strictly from this JSON. "
            "Do not hallucinate; do not reference any external data.\n\n"
            f"{json.dumps(kpi_snapshot, ensure_ascii=False)}"
            + (f"\n\nPrimary sheet of interest: {sheet_hint}" if sheet_hint else "")
        )
        content = openrouter_chat(
            messages=[
                {"role": "system", "content": INSIGHTS_SYSTEM},
                {"role": "user", "content": user_prompt},
            ],
            model=self.model,
            temperature=0.1
        )
        return content  # already HTML per system prompt
