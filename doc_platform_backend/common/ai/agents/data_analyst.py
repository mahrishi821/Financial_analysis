# common/ai/agents/data_analyst.py
import json
import math
import pandas as pd
from datetime import datetime

class DataAnalyst:
    """
    Takes your stored extracted_text (JSON string or raw string).
    Produces:
      - normalized tables (sheet_name -> DataFrame)
      - computed basic KPIs per sheet
      - “best” numeric table for plotting
    """
    def __init__(self):
        pass

    def _parse_extracted(self, extracted_text):
        # Handles your Excel JSON shape like: {"data": {"Sheet1": [...], ...}, ...}
        try:
            obj = json.loads(extracted_text)
            # if Excel processor
            if isinstance(obj, dict) and "data" in obj and isinstance(obj["data"], dict):
                return obj["data"]
            # else if generic JSON array
            if isinstance(obj, list):
                return {"Sheet1": obj}
            # fallback: try a generic top-level dict of sheets
            if isinstance(obj, dict):
                return obj
        except Exception:
            # Non-JSON or plain text → return as single sheet text
            return {"RawText": [{"content": extracted_text}]}
        return {"RawText": [{"content": extracted_text}]}

    def _to_df(self, records):
        # records expected as list[dict]
        if not isinstance(records, list) or not records:
            return pd.DataFrame()
        df = pd.DataFrame(records)

        # Convert timestamps in ms to readable dates where possible
        for col in df.columns:
            try:
                # detect ms timestamps (>= 10^12 is often ms)
                if pd.api.types.is_numeric_dtype(df[col]):
                    sample = df[col].dropna()
                    if not sample.empty:
                        v = sample.iloc[0]
                        if v > 10**11:  # crude ms check
                            df[col] = pd.to_datetime(df[col], unit="ms")
            except Exception:
                pass
        return df

    def _numeric_df(self, df: pd.DataFrame):
        if df.empty:
            return df
        # keep numeric or datetime columns for plotting
        keep = []
        for c in df.columns:
            if pd.api.types.is_numeric_dtype(df[c]) or pd.api.types.is_datetime64_any_dtype(df[c]):
                keep.append(c)
        nd = df[keep].copy() if keep else pd.DataFrame()
        return nd

    def _compute_basic_kpis(self, df: pd.DataFrame):
        out = {}
        if df.empty:
            return out
        numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
        for c in numeric_cols:
            series = df[c].dropna()
            if series.empty:
                continue
            out[c] = {
                "count": int(series.count()),
                "sum": float(series.sum()),
                "mean": float(series.mean()),
                "min": float(series.min()),
                "max": float(series.max()),
            }
        return out

    def analyze(self, extracted_text: str):
        sheets_data = self._parse_extracted(extracted_text)

        sheet_frames = {}
        sheet_kpis = {}
        best_for_plot = None

        for sheet_name, records in sheets_data.items():
            df = self._to_df(records)
            sheet_frames[sheet_name] = df
            kpis = self._compute_basic_kpis(df)
            sheet_kpis[sheet_name] = kpis

            num_df = self._numeric_df(df)
            # choose first numeric df with at least 2 numeric columns as default chart source
            if best_for_plot is None and not num_df.empty and len(num_df.columns) >= 2:
                best_for_plot = (sheet_name, num_df)

        return {
            "sheet_frames": sheet_frames,
            "kpis": sheet_kpis,
            "best_for_plot": best_for_plot  # tuple (sheet_name, numeric_df) or None
        }
