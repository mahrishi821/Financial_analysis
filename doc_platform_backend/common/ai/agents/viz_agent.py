# common/ai/agents/viz_agent.py
import base64
import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

class VizAgent:
    """
    Creates one or two useful charts:
      - Line chart for timeseries-like numeric columns
      - Bar chart for key totals if suitable
    Returns base64-embedded PNGs for inlining into HTML.
    """
    def __init__(self):
        pass

    def _fig_to_base64(self):
        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        plt.close()
        buf.seek(0)
        return base64.b64encode(buf.read()).decode()

    def plot_timeseries(self, sheet_name: str, df: pd.DataFrame):
        if df.empty or df.shape[1] < 2:
            return None
        # pick first datetime or index as x; otherwise use row index
        x = None
        for c in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[c]):
                x = df[c]
                break
        if x is None:
            x = range(len(df))
        # pick up to 3 numeric series to avoid clutter
        ycols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
        if not ycols:
            return None
        ycols = ycols[:3]

        plt.figure(figsize=(8, 4.5))
        for c in ycols:
            plt.plot(x, df[c], label=c)
        plt.title(f"{sheet_name}: Trend")
        plt.xlabel("Index" if not hasattr(x, "dt") else "Date")
        plt.ylabel("Value")
        plt.legend()
        return self._fig_to_base64()

    def plot_bar_totals(self, sheet_name: str, df: pd.DataFrame):
        if df.empty:
            return None
        # sum each numeric col and show a bar chart of top 8
        sums = {c: float(df[c].sum()) for c in df.columns if pd.api.types.is_numeric_dtype(df[c])}
        if not sums:
            return None
        items = sorted(sums.items(), key=lambda x: abs(x[1]), reverse=True)[:8]
        labels = [k for k, _ in items]
        values = [v for _, v in items]

        plt.figure(figsize=(8, 4.5))
        plt.bar(labels, values)
        plt.title(f"{sheet_name}: Column Totals")
        plt.xticks(rotation=30, ha="right")
        plt.ylabel("Total")
        return self._fig_to_base64()
