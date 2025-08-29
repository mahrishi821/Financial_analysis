import os
import requests

class FinancialTextClassifier:
    def __init__(self, hf_token: str = None, bart_threshold: float = 0.7):
        """
        hf_token: Hugging Face API token (set via arg or environment variable HF_TOKEN)
        bart_threshold: probability threshold for financial classification
        """
        # self.api_url = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-mnli"
        self.api_url = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
        self.headers = {
            "Authorization": f"Bearer {hf_token or os.environ.get('HF_TOKEN')}"
        }
        self.bart_threshold = bart_threshold

    def is_financial(self, text: str) -> bool:
        """
        Returns True if the text is financial, otherwise False.
        """
        print(f"Inside the FinancialTextClassifier ")
        if not text or not text.strip():
            return False

        payload = {
            "inputs": text,
            "parameters": {"candidate_labels": ["financial", "legal", "medical", "general"]},
        }

        response = requests.post(self.api_url, headers=self.headers, json=payload)
        result = response.json()

        if "labels" not in result:
            # Handle API error
            return False


        top_label, top_score = result["labels"][0], result["scores"][0]
        # print(f"Top label: {top_label}")
        # print(f"Top score: {top_score}")
        return top_label == "financial" and top_score >= self.bart_threshold
