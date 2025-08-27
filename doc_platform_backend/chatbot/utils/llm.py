import os
from openai import OpenAI


class OpenRouterLLM:
    """
    Wrapper for OpenRouter API (OpenAI-compatible) to handle document Q&A.
    """

    def __init__(
        self,
        model: str = "meta-llama/llama-4-maverick:free",
        max_tokens: int = 512,
        temperature: float = 0.3,
    ):
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables.")

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
        )
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    def generate_answer(self, question: str, context: str) -> str:
        """
        Generate an answer grounded in context using the configured LLM.
        """
        prompt = f"""You are a helpful assistant. 
            Answer the following question using ONLY the context provided.
            If the answer is not in the context, reply with "I cannot find that in the document."
            
            Context:
            {context}
            
            Question: {question}
            Answer:
            """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a document Q&A assistant."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error while generating answer: {e}"
