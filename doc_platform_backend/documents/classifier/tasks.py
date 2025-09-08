# classifier/system.py
import re
from abc import ABC, abstractmethod
from typing import Optional, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from ..models import SheetUnit, AuditLog


# ==============================
# Base Classifier Interface
# ==============================
class BaseClassifier(ABC):
    @abstractmethod
    def classify(self, sheet: SheetUnit) -> Tuple[Optional[str], float]:
        """Return (label, confidence)."""
        pass


# ==============================
# Rule-Based Classifier
# ==============================
class RuleBasedClassifier(BaseClassifier):
    DEFAULT_RULES = {
        "cap_table": [
            "shareholder", "shares", "ownership", "%", "class",
            "option", "vesting", "equity structure"
        ],
        "balance_sheet": [
            "assets", "liabilities", "equity", "total assets",
            "total liabilities", "net assets", "retained earnings"
        ],
        "pnl": [
            "revenue", "net income", "profit", "gross profit",
            "operating expense", "cost of goods", "ebitda", "margin"
        ],
        "cash_flow": [
            "cash flow", "net cash", "operating activities",
            "investing", "financing", "free cash flow"
        ],
    }

    WEIGHTS = {
        "sheet_name": 0.5,
        "header_rows": 0.3,
        "pre_header_context": 0.1,
        "sample_rows": 0.05,
        # structural
        "row_count": 0.05,
        "col_count": 0.05,
        "table_count": 0.02,
    }

    def __init__(self, rules: dict[str, list[str]] | None = None):
        self.rules = rules or self.DEFAULT_RULES

    def _flatten_text(self, rows: list[list[str]]) -> str:
        return " ".join(" ".join(map(str, r)) for r in rows if r).lower()

    def classify(self, sheet: SheetUnit) -> Tuple[Optional[str], float]:
        scores = {label: 0.0 for label in self.rules}

        # --- Textual signals ---
        header_text = self._flatten_text(sheet.header_rows or [])
        sample_text = self._flatten_text(sheet.sample_rows or [])
        pre_header_text = self._flatten_text(sheet.metadata.get("pre_header_context", []))
        sheet_name_text = sheet.sheet_name.lower() if sheet.sheet_name else ""

        signals = {
            "sheet_name": sheet_name_text,
            "header_rows": header_text,
            "sample_rows": sample_text,
            "pre_header_context": pre_header_text,
        }

        # --- Structural signals ---
        struct_signals = {
            "row_count": sheet.row_count,
            "col_count": sheet.col_count,
            "table_count": sheet.metadata.get("table_count", 1),
        }

        # --- Weighted scoring (text) ---
        for label, keywords in self.rules.items():
            for source, text in signals.items():
                if not text:
                    continue
                for kw in keywords:
                    scores[label] += text.count(kw) * self.WEIGHTS[source]

        # --- Structural heuristics ---
        # Cap tables: wide tables, many columns
        if struct_signals["col_count"] > 5 and struct_signals["row_count"] > 5:
            scores["cap_table"] += self.WEIGHTS["col_count"] + self.WEIGHTS["row_count"]

        # Balance sheet: usually ~2–4 columns
        if 2 <= struct_signals["col_count"] <= 4:
            scores["balance_sheet"] += self.WEIGHTS["col_count"]

        # Cash flow: tall (many rows)
        if struct_signals["row_count"] > 30:
            scores["cash_flow"] += self.WEIGHTS["row_count"]

        # P&L: no longer using charts

        # --- Pick best ---
        top = max(scores, key=scores.get)
        if scores[top] == 0:
            return None, 0.0

        total = sum(scores.values())
        confidence = scores[top] / (total + 1e-9)

        return top, confidence


# ==============================
# ML Classifier (TF-IDF + Logistic Regression)
# ==============================
class MLClassifier(BaseClassifier):
    def __init__(self):
        # Load pretrained model from disk in production
        self.vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
        self.model = LogisticRegression(max_iter=500)
        self.is_trained = False

    def _extract_text(self, sheet: SheetUnit) -> str:
        parts = []
        parts.append(sheet.sheet_name or "")
        for rows in (sheet.header_rows, sheet.sample_rows, sheet.metadata.get("pre_header_context", [])):
            if rows:
                parts.append(" ".join(" ".join(map(str, r)) for r in rows))
        return " ".join(parts).lower()

    def _extract_features(self, sheets: list[SheetUnit]):
        texts = [self._extract_text(s) for s in sheets]
        X_text = self.vectorizer.fit_transform(texts)

        # Add structural features
        struct_feats = np.array([
            [s.row_count, s.col_count, s.metadata.get("table_count", 1)]
            for s in sheets
        ])
        # Concatenate sparse + dense
        from scipy.sparse import hstack
        return hstack([X_text, struct_feats])

    def train(self, sheets: list[SheetUnit]):
        labels = [s.classification for s in sheets]

        X = self._extract_features(sheets)
        self.model.fit(X, labels)
        self.is_trained = True

    def classify(self, sheet: SheetUnit) -> Tuple[Optional[str], float]:
        if not self.is_trained:
            return None, 0.0

        text = self._extract_text(sheet)
        X_text = self.vectorizer.transform([text])
        struct_feats = np.array([
            [sheet.row_count, sheet.col_count, sheet.metadata.get("table_count", 1)]
        ])
        from scipy.sparse import hstack
        X = hstack([X_text, struct_feats])

        proba = self.model.predict_proba(X)[0]
        idx = np.argmax(proba)
        label = self.model.classes_[idx]
        return label, float(proba[idx])


# ==============================
# Orchestrator Pipeline
# ==============================
class SheetClassifier:
    """Pipeline combining multiple classifiers."""

    def __init__(self, classifiers: list[BaseClassifier] | None = None):
        # Order: rule first, ML second
        self.classifiers = classifiers or [RuleBasedClassifier(), MLClassifier()]

    def classify(self, sheet_id: int) -> str:
        sheet = SheetUnit.objects.get(id=sheet_id)

        for clf in self.classifiers:
            label, confidence = clf.classify(sheet)
            if label and confidence >= 0.65:  # threshold
                sheet.classification = label
                sheet.classification_confidence = float(confidence)
                sheet.save()
                AuditLog.objects.create(
                    sheet_unit=sheet,
                    action=f"classified_{clf.__class__.__name__.lower()}",
                    details={"label": label, "confidence": confidence},
                )
                print(f"label {label}")
                return label

        # Fallback: unknown
        sheet.classification = "unknown"
        sheet.classification_confidence = 0.0
        sheet.save()
        AuditLog.objects.create(sheet_unit=sheet, action="classified_none", details={})
        return "unknown"
