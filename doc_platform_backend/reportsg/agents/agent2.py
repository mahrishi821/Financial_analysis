import math
import random
import statistics
from datetime import datetime
from collections import defaultdict
from typing import Any, Dict, List, Tuple, Optional


class ChartGeneratorAgent:
    """
    Agent 4:
    Converts structured financial tables (from Agent3) into chart configurations.
    """

    COLOR_PALETTE = [
        "#1F7A8C", "#BFDBF7", "#E1E5F2", "#022B3A",
        "#0F4C5C", "#2A9D8F", "#E76F51", "#F4A261",
        "#264653", "#4ECDC4", "#FFE66D", "#6A0572",
        "#7678ED", "#F18701", "#F35B04", "#17C3B2",
        "#FFCB77", "#FE6D73", "#3D348B", "#7F8695",
        "#99C1DE", "#5C80BC", "#9FD356", "#FF6B6B",
        "#3A86FF", "#8338EC", "#FB5607", "#FF006E",
    ]

    SUPPORTED_TYPES = {
        "line", "bar", "area", "stacked_bar", "stacked_area",
        "scatter", "pie", "donut", "histogram", "box", "bubble",
    }

    # ------------------------- Helpers -------------------------

    def _is_number(self, x: Any) -> bool:
        if x is None:
            return False
        if isinstance(x, (int, float)) and not math.isnan(x):
            return True
        if isinstance(x, str):
            try:
                float(x.replace(",", ""))
                return True
            except Exception:
                return False
        return False

    def _to_float(self, x: Any) -> Optional[float]:
        if x is None:
            return None
        if isinstance(x, (int, float)):
            if isinstance(x, float) and math.isnan(x):
                return None
            return float(x)
        if isinstance(x, str):
            try:
                return float(x.replace(",", ""))
            except Exception:
                return None
        return None

    def _parse_date(self, x: Any) -> Optional[str]:
        if x is None:
            return None
        if isinstance(x, datetime):
            return x.date().isoformat()
        if isinstance(x, str):
            candidates = [
                "%Y-%m-%d", "%Y/%m/%d",
                "%d-%m-%Y", "%d/%m/%Y",
                "%m-%d-%Y", "%m/%d/%Y",
                "%Y-%m", "%Y/%m",
            ]
            for fmt in candidates:
                try:
                    dt = datetime.strptime(x[:10], fmt)
                    if fmt in ("%Y-%m", "%Y/%m"):
                        return f"{dt.year:04d}-{dt.month:02d}-01"
                    return dt.date().isoformat()
                except Exception:
                    continue
        return None

    def _infer_column_type(self, values: List[Any]) -> str:
        date_hits = sum(1 for v in values if self._parse_date(v) is not None)
        if date_hits >= max(2, int(0.6 * len(values))):
            return "date"
        num_hits = sum(1 for v in values if self._is_number(v))
        if num_hits >= max(2, int(0.6 * len(values))):
            return "numeric"
        return "categorical"

    def _normalize_y(self, y_meta: Any) -> List[str]:
        if y_meta is None:
            return []
        if isinstance(y_meta, str):
            return [y_meta]
        if isinstance(y_meta, list):
            return [str(c) for c in y_meta if c]
        return []

    def _titleize(self, s: str) -> str:
        return s.replace("_", " ").title()

    def _unique_colors(self, n: int) -> List[str]:
        if n <= len(self.COLOR_PALETTE):
            return self.COLOR_PALETTE[:n]
        times = (n + len(self.COLOR_PALETTE) - 1) // len(self.COLOR_PALETTE)
        return (self.COLOR_PALETTE * times)[:n]

    def _basic_metrics(self, values: List[Optional[float]]) -> Dict[str, Any]:
        clean = [v for v in values if v is not None]
        if not clean:
            return {"count": 0}
        try:
            return {
                "count": len(clean),
                "min": min(clean),
                "max": max(clean),
                "mean": statistics.fmean(clean),
                "median": statistics.median(clean),
                "sum": sum(clean),
            }
        except Exception:
            return {"count": len(clean), "sum": sum(clean)}

    def _records_from_table(self, columns: List[str], rows: List[List[Any]]) -> List[Dict[str, Any]]:
        return [dict(zip(columns, r)) for r in rows]

    # ------------------------- Chart Builders -------------------------

    def _build_line_chart(self, table, records, x, y_list, chart_type, stacked=False, filled=False):
        # reuse shared XY builder
        series, metrics, enc = self._build_xy_series(records, x, y_list)
        return {
            "table": table,
            "title": f"{self._titleize(table)} ({chart_type})",
            "type": chart_type,
            "x": x,
            "y": y_list,
            "series": series,
            "options": {"stacked": stacked, "filled": filled},
            "encodings": enc,
            "metrics": metrics,
        }

    def _build_xy_series(self, records, x, y_list):
        colors = self._unique_colors(len(y_list))
        series = []
        metrics = {}
        coltype_x = self._infer_column_type([r.get(x) for r in records])

        for idx, y in enumerate(y_list):
            pts = []
            for r in records:
                xv = r.get(x)
                yv = self._to_float(r.get(y))
                if coltype_x == "date":
                    xv = self._parse_date(xv) or xv
                if xv is None or yv is None:
                    continue
                pts.append((xv, yv))
            series.append({"label": y, "data": pts, "color": colors[idx]})
            metrics[y] = self._basic_metrics([p[1] for p in pts])

        return series, metrics, {"x_title": self._titleize(x), "y_title": ", ".join(self._titleize(y) for y in y_list)}

    # (similar private methods for scatter, bubble, pie, histogram, box…)

    # ------------------------- Main Entrypoint -------------------------

    def generate_charts(self, tables_json: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Convert Agent3's tables_json into chart configs.
        """
        if not tables_json:
            return []

        results, seen = [], set()

        for table_name, table in tables_json.items():
            columns = table.get("columns", [])
            rows = table.get("rows", [])
            metadata = table.get("metadata", {}) or {}
            if not columns or not rows:
                continue

            records = self._records_from_table(columns, rows)
            x = metadata.get("x")
            y_list = self._normalize_y(metadata.get("y"))
            suggestions = metadata.get("chart_suggestions", [])

            chart_type = random.choice(suggestions) if suggestions else "line"

            if not x:
                col_types = {c: self._infer_column_type([r.get(c) for r in records]) for c in columns}
                x = next((c for c, t in col_types.items() if t == "date"), columns[0])

            if not y_list:
                y_list = [c for c in columns if c != x and self._infer_column_type([r.get(c) for r in records]) == "numeric"]

            if not y_list:
                continue

            key = (table_name, chart_type, x, tuple(sorted(y_list)))
            if key in seen:
                continue

            # Dispatch chart builder
            cfg = None
            if chart_type in ("line", "bar", "area", "stacked_bar", "stacked_area"):
                stacked = "stacked" in chart_type
                filled = "area" in chart_type
                cfg = self._build_line_chart(table_name, records, x, y_list, chart_type, stacked, filled)

            # TODO: add other chart builders here (scatter, pie, donut, histogram, box, bubble)

            if cfg:
                results.append(cfg)
                seen.add(key)

        return results
