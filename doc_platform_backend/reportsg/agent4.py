# app/agent4.py

from __future__ import annotations
import math
import statistics
from collections import defaultdict, Counter
from datetime import datetime
from typing import Any, Dict, Iterable, List, Tuple, Optional
import random
# ---- Color palette (long list, includes your requested hues) -----------------
COLOR_PALETTE = [
    "#1F7A8C", "#BFDBF7", "#E1E5F2", "#022B3A",
    "#0F4C5C", "#2A9D8F", "#E76F51", "#F4A261",
    "#264653", "#4ECDC4", "#FFE66D", "#6A0572",
    "#7678ED", "#F18701", "#F35B04", "#17C3B2",
    "#FFCB77", "#FE6D73", "#3D348B", "#7F8695",
    "#99C1DE", "#5C80BC", "#9FD356", "#FF6B6B",
    "#3A86FF", "#8338EC", "#FB5607", "#FF006E",
]

# ------------------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------------------

def _is_number(x: Any) -> bool:
    if x is None:
        return False
    if isinstance(x, (int, float)) and not math.isnan(x):
        return True
    # allow numeric-like strings
    if isinstance(x, str):
        try:
            float(x.replace(",", ""))  # tolerate "1,234.56"
            return True
        except Exception:
            return False
    return False

def _to_float(x: Any) -> Optional[float]:
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

def _parse_date(x: Any) -> Optional[str]:
    """
    Normalize date-like values to ISO date string (YYYY-MM-DD) if possible.
    """
    if x is None:
        return None
    if isinstance(x, (datetime, )):
        return x.date().isoformat()
    if isinstance(x, str):
        # try a few common formats
        candidates = [
            "%Y-%m-%d", "%Y/%m/%d",
            "%d-%m-%Y", "%d/%m/%Y",
            "%m-%d-%Y", "%m/%d/%Y",
            "%Y-%m", "%Y/%m",
        ]
        for fmt in candidates:
            try:
                dt = datetime.strptime(x[:10], fmt)
                # if only year-month, coerce day 01
                if fmt in ("%Y-%m", "%Y/%m"):
                    return f"{dt.year:04d}-{dt.month:02d}-01"
                return dt.date().isoformat()
            except Exception:
                continue
    return None

def _infer_col_type(values: Iterable[Any]) -> str:
    """
    Infer column type: "date", "numeric", or "categorical"
    """
    vals = list(values)
    # check date-like
    date_hits = sum(1 for v in vals if _parse_date(v) is not None)
    if date_hits >= max(2, int(0.6 * len(vals))):  # majority look like dates
        return "date"
    # check numeric
    num_hits = sum(1 for v in vals if _is_number(v))
    if num_hits >= max(2, int(0.6 * len(vals))):
        return "numeric"
    return "categorical"

def _records_from_table(columns: List[str], rows: List[List[Any]]) -> List[Dict[str, Any]]:
    return [dict(zip(columns, r)) for r in rows]

def _normalize_y(y_meta: Any) -> List[str]:
    if y_meta is None:
        return []
    if isinstance(y_meta, str):
        return [y_meta]
    if isinstance(y_meta, list):
        # only keep non-empty strings
        return [str(c) for c in y_meta if c]
    return []

def _unique_colors(n: int) -> List[str]:
    # repeat palette if needed but keep per-chart uniqueness until we exhaust the list
    if n <= len(COLOR_PALETTE):
        return COLOR_PALETTE[:n]
    times = (n + len(COLOR_PALETTE) - 1) // len(COLOR_PALETTE)
    extended = (COLOR_PALETTE * times)[:n]
    return extended

def _basic_metrics(series_vals: List[Optional[float]]) -> Dict[str, Any]:
    clean = [v for v in series_vals if v is not None]
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

def _dedupe_key(table: str, chart_type: str, x: str, y_list: List[str]) -> Tuple:
    return (table, chart_type, x, tuple(sorted(y_list)))

def _titleize(s: str) -> str:
    return s.replace("_", " ").title()

# ------------------------------------------------------------------------------
# Chart builders
# ------------------------------------------------------------------------------

def _build_xy_series(records: List[Dict[str, Any]], x: str, y_list: List[str]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    """
    Returns: (series_list, series_metrics, encodings)
    - series_list: [{label, data, color}]
    - series_metrics: {label: metrics}
    - encodings: axis titles etc.
    """
    colors = _unique_colors(len(y_list))
    series = []
    metrics = {}
    for idx, y in enumerate(y_list):
        pts = []
        coltype_x = _infer_col_type([r.get(x) for r in records])
        for r in records:
            xv = r.get(x)
            yv = _to_float(r.get(y))
            if coltype_x == "date":
                xv = _parse_date(xv)
            # keep original categorical/date string if parse failed
            if xv is None:
                xv = r.get(x)
            if yv is None:
                continue
            pts.append((xv, yv))

        series.append({
            "label": y,
            "data": pts,
            "color": colors[idx],
        })
        metrics[y] = _basic_metrics([p[1] for p in pts])

    enc = {
        "x_title": _titleize(x),
        "y_title": ", ".join(_titleize(y) for y in y_list),
    }
    return series, metrics, enc

def _build_line_bar_area(table_name, records, x, y_list, chart_type, stacked=False, filled=False):
    series, metrics, enc = _build_xy_series(records, x, y_list)
    return {
        "table": table_name,
        "title": f"{_titleize(table_name)} ({chart_type.replace('_', ' ').title()})",
        "type": chart_type,  # "line" | "bar" | "area" | "stacked_bar" | "stacked_area"
        "x": x,
        "y": y_list,
        "series": series,
        "options": {
            "stacked": stacked,
            "filled": filled,
            "interpolate": True if chart_type in ("line", "area", "stacked_area") else False,
        },
        "encodings": enc,
        "metrics": metrics,
    }

def _build_scatter(table_name, records, x, y):
    # scatter expects numeric-numeric
    pts = []
    for r in records:
        xv = _to_float(r.get(x))
        yv = _to_float(r.get(y))
        if xv is None or yv is None:
            continue
        pts.append((xv, yv))
    return {
        "table": table_name,
        "title": f"{_titleize(y)} vs {_titleize(x)} (Scatter)",
        "type": "scatter",
        "x": x,
        "y": [y],
        "series": [{"label": y, "data": pts, "color": _unique_colors(1)[0]}],
        "options": {},
        "encodings": {"x_title": _titleize(x), "y_title": _titleize(y)},
        "metrics": {y: _basic_metrics([p[1] for p in pts])},
    }

def _build_bubble(table_name, records, x, y, size_col):
    pts = []
    for r in records:
        xv = _to_float(r.get(x))
        yv = _to_float(r.get(y))
        sv = _to_float(r.get(size_col))
        if xv is None or yv is None or sv is None:
            continue
        pts.append((xv, yv, sv))
    return {
        "table": table_name,
        "title": f"{_titleize(y)} vs {_titleize(x)} by {_titleize(size_col)} (Bubble)",
        "type": "bubble",
        "x": x,
        "y": [y],
        "size": size_col,
        "series": [{"label": f"{y} by {size_col}", "data": pts, "color": _unique_colors(1)[0]}],
        "options": {},
        "encodings": {"x_title": _titleize(x), "y_title": _titleize(y), "size_title": _titleize(size_col)},
        "metrics": {y: _basic_metrics([p[1] for p in pts])},
    }

def _build_pie_or_donut(table_name, records, category_col, value_col, donut=False):
    # aggregate by category
    agg = defaultdict(float)
    for r in records:
        cat = r.get(category_col)
        v = _to_float(r.get(value_col))
        if cat is None or v is None:
            continue
        agg[str(cat)] += v

    items = sorted(agg.items(), key=lambda kv: kv[0])
    colors = _unique_colors(len(items))
    data = []
    total = sum(v for _, v in items) or 1.0
    for (label, v), c in zip(items, colors):
        data.append({"label": label, "value": v, "percentage": (v / total) * 100.0, "color": c})

    return {
        "table": table_name,
        "title": f"{_titleize(value_col)} by {_titleize(category_col)} ({'Donut' if donut else 'Pie'})",
        "type": "donut" if donut else "pie",
        "category": category_col,
        "value": value_col,
        "series": data,  # for pies we provide a flat series
        "options": {"donut": donut},
        "encodings": {"category_title": _titleize(category_col), "value_title": _titleize(value_col)},
        "metrics": {"total": total, "categories": len(items)},
    }

def _build_histogram(table_name, records, value_col, bins: int = 10):
    values = [_to_float(r.get(value_col)) for r in records]
    values = [v for v in values if v is not None]
    if not values:
        return None
    vmin, vmax = min(values), max(values)
    if math.isclose(vmin, vmax):
        # degenerate distribution; put all in one bin
        buckets = [{"bin_start": vmin, "bin_end": vmax, "count": len(values)}]
    else:
        step = (vmax - vmin) / bins
        edges = [vmin + i * step for i in range(bins)] + [vmax]
        counts = [0] * bins
        for v in values:
            # find bin index
            if v == vmax:
                idx = bins - 1
            else:
                idx = min(int((v - vmin) / step), bins - 1)
            counts[idx] += 1
        buckets = [{"bin_start": edges[i], "bin_end": edges[i + 1], "count": counts[i]} for i in range(bins)]

    return {
        "table": table_name,
        "title": f"Distribution of {_titleize(value_col)} (Histogram)",
        "type": "histogram",
        "value": value_col,
        "series": buckets,
        "options": {"bins": bins},
        "encodings": {"x_title": _titleize(value_col), "y_title": "Frequency"},
        "metrics": _basic_metrics(values),
    }

def _build_boxplot(table_name, records, value_col, group_col: Optional[str] = None):
    """
    If group_col provided (categorical), compute box per group; else a single box for the column.
    """
    if group_col:
        groups = defaultdict(list)
        for r in records:
            g = r.get(group_col)
            v = _to_float(r.get(value_col))
            if g is None or v is None:
                continue
            groups[str(g)].append(v)

        series = []
        for g, vals in groups.items():
            if not vals:
                continue
            vals_sorted = sorted(vals)
            q1 = statistics.quantiles(vals_sorted, n=4)[0] if len(vals_sorted) >= 4 else min(vals_sorted)
            q3 = statistics.quantiles(vals_sorted, n=4)[2] if len(vals_sorted) >= 4 else max(vals_sorted)
            series.append({
                "group": g,
                "min": min(vals_sorted),
                "q1": q1,
                "median": statistics.median(vals_sorted),
                "q3": q3,
                "max": max(vals_sorted),
                "count": len(vals_sorted),
            })
        title = f"{_titleize(value_col)} by {_titleize(group_col)} (Box Plot)"
    else:
        vals = [_to_float(r.get(value_col)) for r in records if _to_float(r.get(value_col)) is not None]
        if not vals:
            return None
        vals_sorted = sorted(vals)
        q1 = statistics.quantiles(vals_sorted, n=4)[0] if len(vals_sorted) >= 4 else min(vals_sorted)
        q3 = statistics.quantiles(vals_sorted, n=4)[2] if len(vals_sorted) >= 4 else max(vals_sorted)
        series = [{
            "group": value_col,
            "min": min(vals_sorted),
            "q1": q1,
            "median": statistics.median(vals_sorted),
            "q3": q3,
            "max": max(vals_sorted),
            "count": len(vals_sorted),
        }]
        title = f"{_titleize(value_col)} (Box Plot)"

    return {
        "table": table_name,
        "title": title,
        "type": "box",
        "value": value_col,
        "group": group_col,
        "series": series,
        "options": {},
        "encodings": {"x_title": _titleize(group_col) if group_col else "", "y_title": _titleize(value_col)},
        "metrics": {"groups": len(series)},
    }

# ------------------------------------------------------------------------------
# Main Agent 4
# ------------------------------------------------------------------------------

SUPPORTED_TYPES = {
    "line",
    "bar",
    "area",
    "stacked_bar",
    "stacked_area",
    "scatter",
    "pie",
    "donut",
    "histogram",
    "box",
    # "heatmap" (optional; implement when you have matrix-style tables)
    "bubble",
}


def run_agent4(tables_json: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Convert Agent 3's tables_json into a list of chart configs.
    - Rule-based.
    - Picks ONE random chart type per table from metadata["chart_suggestions"].
    - Falls back to 'line' if missing.
    - Ensures charts have valid x, y.
    - Deduplicates by (table, type, x, y-set).
    """
    if not tables_json:
        return []

    out: List[Dict[str, Any]] = []
    seen = set()

    for table_name, table in tables_json.items():
        columns = table.get("columns", [])
        rows = table.get("rows", [])
        metadata = table.get("metadata", {}) or {}

        if not columns or not rows:
            continue

        records = _records_from_table(columns, rows)
        x = metadata.get("x")
        y_list = _normalize_y(metadata.get("y"))
        suggestions = metadata.get("chart_suggestions", [])

        # pick one random chart type from suggestions (or fallback)
        if suggestions:
            chosen_type = random.choice(suggestions)
        else:
            chosen_type = "line"

        # fallback inference if metadata is incomplete
        if not x and columns:
            col_types = {c: _infer_col_type([r.get(c) for r in records]) for c in columns}
            date_candidates = [c for c, t in col_types.items() if t == "date"]
            x = date_candidates[0] if date_candidates else columns[0]

        if not y_list:
            y_list = [
                c for c in columns
                if c != x and _infer_col_type([r.get(c) for r in records]) == "numeric"
            ]

        if not y_list:
            continue

        # Dedup key
        key = _dedupe_key(table_name, chosen_type, x, y_list)
        if key in seen:
            continue

        cfg = None
        s = chosen_type.lower().strip()

        if s in ("line", "bar", "area", "stacked_bar", "stacked_area"):
            stacked = s in ("stacked_bar", "stacked_area")
            filled = s in ("area", "stacked_area")
            cfg = _build_line_bar_area(table_name, records, x, y_list, s, stacked=stacked, filled=filled)

        elif s == "scatter":
            cfg = _build_scatter(table_name, records, x, y_list[0])

        elif s in ("pie", "donut"):
            x_type = _infer_col_type([r.get(x) for r in records])
            cat_col = x if x_type == "categorical" else None
            if not cat_col:
                for c in columns:
                    if c == x or c in y_list:
                        continue
                    if _infer_col_type([r.get(c) for r in records]) == "categorical":
                        cat_col = c
                        break
            if cat_col:
                cfg = _build_pie_or_donut(table_name, records, cat_col, y_list[0], donut=(s == "donut"))

        elif s == "histogram":
            value_col = next((c for c in y_list if _infer_col_type([r.get(c) for r in records]) == "numeric"), None)
            if value_col:
                cfg = _build_histogram(table_name, records, value_col)

        elif s == "box":
            x_type = _infer_col_type([r.get(x) for r in records])
            if x_type == "categorical":
                cfg = _build_boxplot(table_name, records, y_list[0], group_col=x)
            else:
                cfg = _build_boxplot(table_name, records, y_list[0], group_col=None)

        elif s == "bubble":
            numeric_cols = [c for c in columns if _infer_col_type([r.get(c) for r in records]) == "numeric"]
            if len(numeric_cols) >= 3:
                x_c = x if x in numeric_cols else numeric_cols[0]
                y_c = y_list[0] if y_list[0] in numeric_cols else numeric_cols[1]
                size_c = next((c for c in numeric_cols if c not in (x_c, y_c)), numeric_cols[2])
                cfg = _build_bubble(table_name, records, x_c, y_c, size_c)

        if cfg:
            out.append(cfg)
            seen.add(key)

    return out
