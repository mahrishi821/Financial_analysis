import os
import datetime
import logging
from typing import Optional, Dict, Any, List
import autogen
import markdown

API_KEY = os.getenv("AUTOGEN_API_KEY", "YOUR_API_KEY")

llm_config = {
    "config_list": [
        {
            "model": "meta-llama/llama-4-maverick:free",
            "api_key": os.getenv("OPENROUTER_API_KEY"),
            "base_url": "https://openrouter.ai/api/v1"
        }
    ]
}



financial_assistant = autogen.AssistantAgent(
    name="Financial_assistant",
    llm_config=llm_config,
)

research_assistant = autogen.AssistantAgent(
    name="Researcher",
    llm_config=llm_config,
)

writer = autogen.AssistantAgent(
    name="writer",
    llm_config=llm_config,
    system_message="""
        You are a professional writer, known for
        your insightful and engaging finance reports.
        You transform complex concepts into compelling narratives.
        Include all metrics provided to you as context in your analysis.
        Only answer with the financial report written in markdown directly, do not include a markdown language block indicator.
        Only return your final work without additional comments.
        """,
)

export_assistant = autogen.AssistantAgent(
    name="Exporter",
    llm_config=llm_config,
)

critic = autogen.AssistantAgent(
    name="Critic",
    is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
    llm_config=llm_config,
    system_message="You are a critic. You review the work of the writer and provide constructive feedback.",
)

legal_reviewer = autogen.AssistantAgent(
    name="Legal_Reviewer",
    llm_config=llm_config,
    system_message="You are a legal reviewer. Provide concise legal compliance feedback (<=3 bullet points). Begin with role."
)

consistency_reviewer = autogen.AssistantAgent(
    name="Consistency_reviewer",
    llm_config=llm_config,
    system_message="You are a consistency reviewer. Ensure numbers and text are consistent."
)

textalignment_reviewer = autogen.AssistantAgent(
    name="Text_lignment_reviewer",
    llm_config=llm_config,
    system_message="You are a text alignment reviewer. Ensure meaning aligns with numbers."
)

completion_reviewer = autogen.AssistantAgent(
    name="Completion_Reviewer",
    llm_config=llm_config,
    system_message=(
        "You are a content completion reviewer. Verify that the report contains: "
        "a news report about each asset, ratios, future scenarios, a comparison table and at least a figure."
    )
)

meta_reviewer = autogen.AssistantAgent(
    name="Meta_Reviewer",
    llm_config=llm_config,
    system_message="You are a meta reviewer, aggregate other reviewers' feedback and give final suggestions."
)


# Register nested reviews under critic (mirrors your uploaded file's orchestration)
def reflection_message(recipient, messages, sender, config):
    # This reflection approach attempts to take the last message written by the 'sender'
    try:
        return f"Review the following content.\n\n {recipient.chat_messages_for_summary(sender)[-1]['content']}"
    except Exception:
        # fallback if method signatures differ
        return "Review the most recent content."

review_chats = [
    {
        "recipient": legal_reviewer, "message": reflection_message,
        "summary_method": "reflection_with_llm",
        "summary_args": {"summary_prompt": "Return review into a JSON object only:{'Reviewer':'','Review':''}"},
        "max_turns": 1
    },
    {
        "recipient": textalignment_reviewer, "message": reflection_message,
        "summary_method": "reflection_with_llm",
        "summary_args": {"summary_prompt": "Return review into a JSON object only:{'Reviewer':'','Review':''}"},
        "max_turns": 1
    },
    {
        "recipient": consistency_reviewer, "message": reflection_message,
        "summary_method": "reflection_with_llm",
        "summary_args": {"summary_prompt": "Return review into a JSON object only:{'Reviewer':'','Review':''}"},
        "max_turns": 1
    },
    {
        "recipient": completion_reviewer, "message": reflection_message,
        "summary_method": "reflection_with_llm",
        "summary_args": {"summary_prompt": "Return review into a JSON object only:{'Reviewer':'','Review':''}"},
        "max_turns": 1
    },
    {
        "recipient": meta_reviewer,
        "message": "Aggregate feedback from all reviewers and give final suggestions on the writing.",
        "max_turns": 1
    }
]

try:
    critic.register_nested_chats(review_chats, trigger=writer)
except Exception as e:
    print(str(e))
    # Some autogen versions may register differently — log and continue; the pipeline may still work.
    # logger.info("Could not register nested chats using critic.register_nested_chats; continuing.")


# A user proxy agent that doesn't require interactive human input
user_proxy_auto = autogen.UserProxyAgent(
    name="User_Proxy_Auto",
    human_input_mode="NEVER",
    is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={
        "last_n_messages": 3,
        "work_dir": "/coding/asset_analysis_{analysis.id}",
        "use_docker": False,
    },
)


# === Primary function to run the multi-agent workflow ===
def run_asset_analysis(asset_query: str, work_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Run the multi-agent pipeline for the provided asset_query (tickers or natural language).
    Parameters:
        asset_query: str - e.g. "AAPL, MSFT" or "Apple and Microsoft"
        work_dir: Optional[str] - where agents can save figures/files (defaults to ./coding)
    Returns:
        dict: structured result { status: 'success'|'error', ... }
    """
    if not asset_query or not isinstance(asset_query, str):
        return {"status": "error", "message": "asset_query must be a non-empty string."}

    try:
        # Ensure work_dir exists
        if work_dir is None:
            work_dir = os.path.abspath("./coding")
        os.makedirs(work_dir, exist_ok=True)

        date_str = datetime.datetime.now().strftime("%Y-%m-%d")

        # Task messages (adapted from your uploaded streamlit flow)
        financial_tasks = [
            f"""Today is the {date_str}.
            What are the current stock prices of {asset_query}, and how is the performance over the past 6 months in terms of percentage change?
            Start by retrieving the full name of each stock and use it for all future requests.
            Prepare a figure of the normalized price of these stocks and save it to a file named normalized_prices.png in the working directory. Include information about, if applicable:
            * P/E ratio
            * Forward P/E
            * Dividends
            * Price to book
            * Debt/Eq
            * ROE
            * Analyze the correlation between the stocks
            Do not use a solution that requires an API key.
            If some of the data does not makes sense, such as a price of 0, change the query and re-try.""",

            """Investigate possible reasons of the stock performance leveraging market news headlines from Bing News or Google Search. Retrieve news headlines using python and return them. Use the full name stocks to retrieve headlines. Retrieve at least 10 headlines per stock. Do not use a solution that requires an API key. Do not perform a sentiment analysis.""",
        ]

        # Initiate chats with the configured agents
        # with_logger = logger.info
        # with_logger(f"Starting multi-agent run for asset_query: {asset_query} in {work_dir}")

        # Compose the chats list similar to your original file
        chats_payload = [
            {
                "sender": user_proxy_auto,
                "recipient": financial_assistant,
                "message": financial_tasks[0],
                "silent": False,
                "summary_method": "reflection_with_llm",
                "summary_args": {
                    "summary_prompt": (
                        "Return the stock prices of the stocks, their performance and all other metrics "
                        "into a JSON object only. Provide the name of all figure files created. Provide the full name of each stock."
                    ),
                },
                "clear_history": False,
                "carryover": (
                    "Wait for confirmation of code execution before terminating the conversation. "
                    "Verify that the data is not completely composed of NaN values. Reply TERMINATE in the end when everything is done."
                ),
            },
            {
                "sender": user_proxy_auto,
                "recipient": research_assistant,
                "message": financial_tasks[1],
                "silent": False,
                "summary_method": "reflection_with_llm",
                "summary_args": {
                    "summary_prompt": (
                        "Provide the news headlines as a paragraph for each stock, be precise but do not consider news events that are vague, return the result as a JSON object only."
                    )
                },
                "clear_history": False,
                "carryover": "Wait for confirmation of code execution before terminating the conversation. Reply TERMINATE in the end when everything is done.",
            },
            {
                "sender": critic,
                "recipient": writer,
                "message": (
                    "Develop an engaging financial report using all information provided, include the normalized_prices.png figure "
                    "and other figures if provided. Create a table comparing all the fundamental ratios and data. Provide comments and descriptions. "
                    "Provide analysis and summary for each stock and possible future scenarios. Return the final report in markdown only."
                ),
                "carryover": "I want to include a figure and a table of the provided data in the financial report.",
                "max_turns": 2,
                "summary_method": "last_msg",
            }
        ]

        # Tell autogen to write output files to 'work_dir' (some versions allow a working dir param; if not, agents should write to relative path)
        # If autogen supports per-run options, pass them. If not, agents should save to work_dir internally.
        chat_results = autogen.initiate_chats(chats_payload)

        # Extract the final writer content (best-effort)
        try:
            final_writer_content = chat_results[-1].chat_history[-1]["content"]
        except Exception:
            # fallback extraction
            final_writer_content = None
        html_report = ""
        if final_writer_content:
            html_body = markdown.markdown(final_writer_content, extensions=["tables", "fenced_code"])
            html_report = f"""
                    <html>
                    <head>
                        <meta charset="utf-8"/>
                        <title>Financial Report</title>
                        <style>
                            body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                            table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
                            th, td {{ border: 1px solid #ddd; padding: 8px; }}
                            th {{ background-color: #f4f4f4; }}
                            img {{ max-width: 100%; height: auto; }}
                        </style>
                    </head>
                    <body>
                        {html_body}
                    </body>
                    </html>
                    """

        # Attempt to detect generated figures in the work_dir (common filename used in your tasks)
        found_figures: List[str] = []
        normalized_path = os.path.join(work_dir, "normalized_prices.png")
        if os.path.exists(normalized_path):
            found_figures.append(normalized_path)

        # also scan for other png/pdf outputs
        for fname in os.listdir(work_dir):
            if fname.lower().endswith((".png", ".jpg", ".jpeg", ".pdf")) and fname not in [os.path.basename(p) for p in found_figures]:
                found_figures.append(os.path.join(work_dir, fname))

        result = {
            "report": html_report,
            "figures": found_figures,
            "chat_results": chat_results,
             }

        return result

    except Exception as e:
        return {'error':str(e)}



