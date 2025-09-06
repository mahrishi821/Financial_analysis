import os
import requests
from transformers import AutoTokenizer

class FinancialDocClassifier:
    def __init__(self, prob_threshold: float = 0.6):
        self.api_url = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
        self.headers = {
            "Authorization": f"Bearer {os.environ.get('HF_TOKEN')}"
        }
        self.prob_threshold = prob_threshold

        self.categories = [
            # Core Financial Statements
            "balance sheet", "income statement", "profit and loss statement",
            "cash flow statement", "statement of changes in equity", "financial summary",

            # Periodic Reports
            "annual report", "quarterly report", "monthly report", "management report",
            "budget report", "forecast report",

            # Compliance & Audit
            "audit report", "tax document", "tax return", "compliance report",
            "regulatory filing", "SEC filing", "10-K report", "10-Q report",

            # Transactional Documents
            "invoice", "receipt", "purchase order", "sales order",
            "bill of lading", "shipping document", "credit note", "debit note",

            # Payroll & HR Finance
            "payroll record", "salary slip", "pension statement", "employee expense report",

            # Financing & Investments
            "loan agreement", "loan repayment schedule", "debt covenant", "credit report",
            "investment report", "cap table", "shareholder agreement", "equity research report",
            "prospectus", "bond indenture", "fund fact sheet",

            # Banking & Treasury
            "bank statement", "reconciliation statement", "treasury report", "cash management report",

            # Contracts & Legal Finance Docs
            "merger agreement", "acquisition agreement", "partnership agreement", "financial lease agreement",

            # Others
            "general ledger", "trial balance", "voucher", "chart of accounts",
            "financial disclosure", "insurance claim", "grant report", "other"
        ]

        self.tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-mnli")

    def chunk_text(self, text: str, max_length: int = 512):
        tokens = self.tokenizer.encode(text, add_special_tokens=False)
        for i in range(0, len(tokens), max_length):
            yield self.tokenizer.decode(tokens[i:i+max_length])

    def classify(self, text: str, top_n: int = 3) -> dict:
        """Classify input text into financial document type."""
        if not text or not text.strip():
            return {"predicted": "other", "nearest": "other", "confidence": 0.0, "top_n": []}

        try:
            predictions = {}

            for chunk in self.chunk_text(text):
                payload = {
                    "inputs": chunk,
                    "parameters": {"candidate_labels": self.categories}
                }
                response = requests.post(self.api_url, headers=self.headers, json=payload)
                result = response.json()

                if "error" in result:
                    print(f"[Error] {result['error']}")
                    continue

                for label, score in zip(result["labels"], result["scores"]):
                    predictions[label] = predictions.get(label, 0) + score

            if not predictions:
                return {"predicted": "other", "nearest": "other", "confidence": 0.0, "top_n": []}

            # Sort predictions
            sorted_preds = sorted(predictions.items(), key=lambda x: x[1], reverse=True)

            best_label, best_score = sorted_preds[0]

            return {
                "predicted": best_label if best_score >= self.prob_threshold else "other",
                "nearest": best_label,
                "confidence": round(best_score, 3),

            }

        except Exception as e:
            return {
                "predicted": "error", "nearest": "error", "confidence": 0.0,
                "message": str(e)
            }
