import os
import datetime
import markdown
import autogen
from typing import Optional, Dict, Any, List


class FinancialAnalysisPipeline:
    def __init__(self, llm_config: dict):
        self.llm_config = llm_config
        self._init_agents()
        self._register_review_chains()

    def _init_agents(self):
        """Initialize all assistants and reviewers."""
        self.financial_assistant = autogen.AssistantAgent(name="FinancialAssistant", llm_config=self.llm_config)
        self.research_assistant = autogen.AssistantAgent(name="ResearchAssistant", llm_config=self.llm_config)
        self.writer = autogen.AssistantAgent(
            name="Writer",
            llm_config=self.llm_config,
            system_message=(
                "You are a professional finance writer..."
            )
        )
        self.critic = autogen.AssistantAgent(
            name="Critic",
            llm_config=self.llm_config,
            is_termination_msg=lambda x: "TERMINATE" in x.get("content", ""),
            system_message="You are a critic reviewing reports."
        )
        # Other reviewers...
        self.legal_reviewer = autogen.AssistantAgent(name="LegalReviewer", llm_config=self.llm_config)
        self.consistency_reviewer = autogen.AssistantAgent(name="ConsistencyReviewer", llm_config=self.llm_config)
        self.textalignment_reviewer = autogen.AssistantAgent(name="TextAlignmentReviewer", llm_config=self.llm_config)
        self.completion_reviewer = autogen.AssistantAgent(name="CompletionReviewer", llm_config=self.llm_config)
        self.meta_reviewer = autogen.AssistantAgent(name="MetaReviewer", llm_config=self.llm_config)

        self.user_proxy_auto = autogen.UserProxyAgent(
            name="UserProxy",
            human_input_mode="NEVER",
            code_execution_config={"last_n_messages": 3, "work_dir": "./coding", "use_docker": False},
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        )

    def _register_review_chains(self):
        """Register nested review workflow under critic."""
        def reflection_message(recipient, messages, sender, config):
            try:
                return f"Review the following content.\n\n {recipient.chat_messages_for_summary(sender)[-1]['content']}"
            except Exception:
                return "Review the most recent content."

        review_chats = [
            {"recipient": self.legal_reviewer, "message": reflection_message, "max_turns": 1},
            {"recipient": self.textalignment_reviewer, "message": reflection_message, "max_turns": 1},
            {"recipient": self.consistency_reviewer, "message": reflection_message, "max_turns": 1},
            {"recipient": self.completion_reviewer, "message": reflection_message, "max_turns": 1},
            {"recipient": self.meta_reviewer, "message": "Aggregate reviewer feedback.", "max_turns": 1},
        ]

        try:
            self.critic.register_nested_chats(review_chats, trigger=self.writer)
        except Exception as e:
            print(f"Review registration failed: {e}")

    def _build_tasks(self, asset_query: str) -> List[dict]:
        """Prepare task prompts for agents."""
        today = datetime.datetime.now().strftime("%Y-%m-%d")

        financial_task = f"""
        Today is {today}.
        Analyze stock performance of {asset_query}...
        """
        news_task = f"Retrieve 10+ recent news headlines for {asset_query}..."

        return [
            {"sender": self.user_proxy_auto, "recipient": self.financial_assistant, "message": financial_task},
            {"sender": self.user_proxy_auto, "recipient": self.research_assistant, "message": news_task},
            {"sender": self.critic, "recipient": self.writer, "message": "Write final markdown report."},
        ]

    def _generate_html_report(self, markdown_text: str) -> str:
        """Convert markdown report to styled HTML."""
        html_body = markdown.markdown(markdown_text, extensions=["tables", "fenced_code"])
        return f"""
        <html>
        <head><meta charset="utf-8"/><title>Financial Report</title></head>
        <body>{html_body}</body>
        </html>
        """

    def _collect_figures(self, work_dir: str) -> List[str]:
        """Collect figure/image file paths from work_dir."""
        figures = []
        for fname in os.listdir(work_dir):
            if fname.lower().endswith((".png", ".jpg", ".jpeg", ".pdf")):
                figures.append(os.path.join(work_dir, fname))
        return figures

    def run_analysis(self, asset_query: str, work_dir: Optional[str] = None) -> Dict[str, Any]:
        """Run  analysis full analysis pipeline."""
        if not asset_query:
            return {"status": "error", "message": "Asset query required."}

        work_dir = work_dir or os.path.abspath("./coding")
        os.makedirs(work_dir, exist_ok=True)

        chats_payload = self._build_tasks(asset_query)
        chat_results = autogen.initiate_chats(chats_payload)

        try:
            final_content = chat_results[-1].chat_history[-1]["content"]
            html_report = self._generate_html_report(final_content)
        except Exception:
            html_report = ""

        return {
            "status": "success",
            "report": html_report,
            "figures": self._collect_figures(work_dir),
            "chat_results": chat_results,
        }
