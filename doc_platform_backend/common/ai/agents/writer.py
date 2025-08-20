# common/ai/agents/writer.py
from markdown2 import markdown

class Writer:
    """
    Composes final HTML by combining:
    - title/meta
    - insights_html (already HTML)
    - KPI table (HTML)
    - charts (base64 <img>)
    - optional raw excerpt (for appendix)
    """
    def __init__(self):
        pass

    def table_html_from_kpis(self, kpis: dict):
        # kpis: {sheet_name: {col: {count, sum, mean, min, max}}}
        parts = []
        for sheet, cols in kpis.items():
            parts.append(f"<h3>{sheet} — Key Metrics</h3>")
            if not cols:
                parts.append("<p>No numeric metrics found.</p>")
                continue
            parts.append('<table border="1" cellpadding="6" cellspacing="0">')
            parts.append("<thead><tr><th>Column</th><th>Count</th><th>Sum</th><th>Mean</th><th>Min</th><th>Max</th></tr></thead><tbody>")
            for col, stats in cols.items():
                parts.append(
                    f"<tr><td>{col}</td><td>{stats.get('count', '')}</td>"
                    f"<td>{round(stats.get('sum', 0), 4)}</td>"
                    f"<td>{round(stats.get('mean', 0), 4)}</td>"
                    f"<td>{round(stats.get('min', 0), 4)}</td>"
                    f"<td>{round(stats.get('max', 0), 4)}</td></tr>"
                )
            parts.append("</tbody></table>")
        return "\n".join(parts)

    def compose_html(self, file_name, file_type, insights_html, kpi_html, charts_base64, raw_excerpt=None):
        imgs = ""
        for title, b64 in charts_base64:
            imgs += f'<div style="margin:16px 0;"><h4>{title}</h4><img alt="{title}" src="data:image/png;base64,{b64}" /></div>'

        raw_section = ""
        if raw_excerpt:
            raw_section = f"""
            <hr>
            <div class="raw">
                <h3>Appendix: Raw Extract (truncated)</h3>
                <pre>{raw_excerpt}</pre>
            </div>
            """

        html = f"""<!DOCTYPE html>
<html>
<head>
  <title>Report - {file_name}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 20px; }}
    h1 {{ color: #2c3e50; }}
    .meta {{ font-size: 14px; color: #555; }}
    .section {{ margin-top: 20px; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ddd; text-align: left; }}
    th {{ background: #f4f6f8; }}
    img {{ max-width: 100%; height: auto; }}
    pre {{ white-space: pre-wrap; word-wrap: break-word; }}
  </style>
</head>
<body>
  <h1>Report for {file_name}</h1>
  <div class="meta"><p><strong>File Type:</strong> {file_type}</p></div>

  <div class="section">
    {insights_html}
  </div>

  <div class="section">
    <h2>Key Metrics</h2>
    {kpi_html}
  </div>

  <div class="section">
    <h2>Visualizations</h2>
    {imgs or "<p>No charts generated.</p>"}
  </div>

  {raw_section}
</body>
</html>"""
        return html
