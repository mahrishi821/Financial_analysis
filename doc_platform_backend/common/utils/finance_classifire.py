import os
import requests
import pandas as pd
from transformers import AutoTokenizer

class FinancialTextClassifier:
    def __init__(self, hf_token: str = None, prob_threshold: float = 0.6):
        self.api_url = "https://api-inference.huggingface.co/models/ProsusAI/finbert"
        self.headers = {
            "Authorization": f"Bearer {hf_token or os.environ.get('HF_TOKEN')}"
        }
        self.prob_threshold = prob_threshold

        # Tokenizer ensures proper chunking
        self.tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")


    def chunk_text(self, text: str, max_length: int = 512):
        """Split text into chunks within model's max length"""
        tokens = self.tokenizer.encode(text, add_special_tokens=False)
        for i in range(0, len(tokens), max_length):
            yield self.tokenizer.decode(tokens[i:i+max_length])

    def is_financial(self, text: str) -> bool:
        try:
            if not text or not text.strip():
                return False

            positive_chunks = 0
            total_chunks = 0

            for chunk in self.chunk_text(text, max_length=510):
                total_chunks += 1
                payload = {"inputs": chunk,
                           "parameters": {"truncation": True, "max_length": 512}}
                response = requests.post(self.api_url, headers=self.headers, json=payload)
                result = response.json()

                if isinstance(result, dict) and "error" in result:
                    continue
                if isinstance(result, list) and len(result) > 0 and isinstance(result[0], list):
                    result = result[0]

                if isinstance(result, list) and result:
                    best = max(result, key=lambda x: x["score"])
                    top_label, top_score = best["label"], best["score"]

                    if top_label in ("neutral", "positive") and top_score >= 0.8:
                        positive_chunks += 1

            print(f"[Decision] {positive_chunks}/{total_chunks} chunks passed")

            # Require at least 2 positive chunks
            return positive_chunks >= 2

        except Exception as e:
            return str(e)
