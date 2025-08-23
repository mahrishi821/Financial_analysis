# app/agent3.py
import json
from common.ai.openrouter_client import openrouter_chat
import re

def run_agent3_pipeline(raw_text):
    """
    Agent 3: Interpret extracted raw text and return:
    1. Summary in HTML format (for reports).
    2. Insights in JSON format (KPIs, anomalies, trends).
    3. Tables in JSON format (chart-worthy, numeric tables only).
    """

    prompt = f"""
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
    # print(f"\n{prompt}")
    try:
        response = openrouter_chat(
            messages=[
                {"role": "system", "content": "You are a financial analysis assistant."},
                {"role": "user", "content": prompt},
            ],
            model="z-ai/glm-4.5-air:free",
            temperature=0.4,
        )
        cleaned = re.sub(r"^```(json)?|```$", "", response.strip(), flags=re.MULTILINE).strip()
        # Ensure response is JSON

        parsed = json.loads(cleaned)
        print(f"parsed:{parsed}")
        return (
            parsed.get("summary_html", "<p>No summary</p>"),
            parsed.get("insights_json", {"kpis": {}, "trends": [], "anomalies": []}),
            parsed.get("tables_json", None),
        )
    except Exception as e:
        print(f"error : {str(e)}")
        return(str(e))


