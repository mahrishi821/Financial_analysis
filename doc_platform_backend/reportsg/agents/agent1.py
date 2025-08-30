# app/agent3.py
import json
import re
from common.ai.openrouter_client import openrouter_chat


class FinancialDocumentInterpreter:
    """
    Agent 3:
    Interprets extracted raw text and produces:
    1. Summary (HTML string for reports)
    2. Insights (KPIs, anomalies, trends in JSON)
    3. Tables (chart-worthy numeric tables in JSON)
    """

    def __init__(self, model: str = "z-ai/glm-4.5-air:free", temperature: float = 0.4):
        self.model = model
        self.temperature = temperature

    def _build_prompt(self, raw_text: str) -> str:
        """Constructs the structured analysis prompt."""
        return f"""
        You are a financial analyst.
        You will be given raw financial document text.

        Your job:
        1. Generate a **detailed executive summary** in valid HTML format.
        2. Extract **insights** (KPIs, trends, anomalies) in JSON format.
        3. Extract any **chart-worthy tables** in JSON format. 
           - Only include numeric tables suitable for plotting graphs.
           - Each table must have "columns", "rows", and "metadata" (with recommended x, y, chart types).
           - If no valid tables, return null.

        Final Output must be valid JSON with this structure:
        {{
          "summary_html": "<p>...</p>",
          "insights_json": {{
            "kpis": {{ "profit_margin": "20%", "growth_rate": "15%" }},
            "trends": ["Revenue increased YoY"],
            "anomalies": ["Cash flow turned negative in Q2"]
          }},
          "tables_json": {{
            "financials": {{
              "columns": ["Year", "Revenue", "Profit"],
              "rows": [[2021, 1000, 200], [2022, 1500, 300]],
              "metadata": {{
                "x": "Year",
                "y": ["Revenue", "Profit"],
                "chart_suggestions": ["line", "bar"]
              }}
            }}
          }}
        }}

        Raw Text:
        {raw_text}
        """

    def _call_model(self, prompt: str) -> str:
        """Send prompt to LLM and return raw response."""
        return openrouter_chat(
            messages=[
                {"role": "system", "content": "You are a financial analysis assistant."},
                {"role": "user", "content": prompt},
            ],
            model=self.model,
            temperature=self.temperature,
        )

    def _clean_response(self, response: str) -> str:
        """Remove markdown fences and whitespace."""
        return re.sub(r"^```(json)?|```$", "", response.strip(), flags=re.MULTILINE).strip()

    def _parse_response(self, response: str) -> dict:
        """Parse response into JSON with fallback."""
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response: {str(e)}")

    def run(self, raw_text: str):
        """
        Orchestrates the full pipeline:
        1. Build prompt
        2. Call model
        3. Clean + parse response
        4. Return structured output
        """
        try:
            prompt = self._build_prompt(raw_text)
            response = self._call_model(prompt)
            cleaned = self._clean_response(response)
            parsed = self._parse_response(cleaned)

            return (
                parsed.get("summary_html", "<p>No summary</p>"),
                parsed.get("insights_json", {"kpis": {}, "trends": [], "anomalies": []}),
                parsed.get("tables_json", None),
            )
        except Exception as e:
            print(f"Agent3 Error: {str(e)}")
            return "<p>Error generating summary</p>", {}, None
