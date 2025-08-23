from common.third_party_integration.doc_paraphraser import DocumentParaphraser
from common.third_party_integration.pdf_paraphraser import Paraphrasepdf
from common.third_party_integration.excel_pharaphraser import ExcelDataProcessor
import os
import pandas as pd
import re

def is_financial_text(text: str) -> bool:
    financial_keywords = [
        # Core financial statements
        "balance sheet", "income statement", "cash flow statement", "statement of changes in equity", "comprehensive income",

        # Accounting basics
        "assets", "liabilities", "equity", "revenue", "expenses", "profit", "loss", "gross margin", "net income", "operating income",
        "ebitda", "ebit", "retained earnings", "depreciation", "amortization", "accounts payable", "accounts receivable", "inventory",
        "cost of goods sold", "cogs", "overheads", "working capital", "current ratio", "quick ratio", "liquidity", "solvency", "going concern",

        # Corporate finance / valuation
        "discounted cash flow", "dcf", "net present value", "npv", "internal rate of return", "irr", "wacc", "capital expenditure", "capex", "opex",
        "return on equity", "roe", "return on assets", "roa", "return on investment", "roi", "enterprise value", "ev", "market capitalization", "dividend",
        "dividend yield", "dividend payout ratio", "earnings yield", "free cash flow", "leverage ratio", "capital structure", "cost of capital",

        # Banking & credit
        "loan", "credit", "interest", "collateral", "default", "leverage", "debt-to-equity", "coverage ratio", "syndicated loan", "bond", "yield",
        "treasury", "commercial paper", "mortgage", "derivatives", "hedging", "credit risk", "counterparty risk", "sovereign risk", "covenants",

        # Investments & securities
        "stock", "shareholder", "equity financing", "ipo", "secondary offering", "valuation", "pe ratio", "price to earnings", "earnings per share", "eps",
        "book value", "market value", "beta", "alpha", "hedge fund", "mutual fund", "etf", "index fund", "portfolio", "diversification",
        "asset allocation", "risk-adjusted return", "sharpe ratio", "treynor ratio", "jensen alpha", "benchmark", "volatility", "liquidity risk",

        # Derivatives & structured products
        "futures", "options", "forwards", "swaps", "cds", "cdo", "structured notes", "securitization", "tranche", "hedge ratio","facility",

        # Risk & insurance
        "underwriting", "premium", "claim", "payout", "loss ratio", "combined ratio", "actuarial", "reinsurance", "catastrophe bond",

        # Regulatory / compliance
        "ifrs", "gaap", "sarbanes-oxley", "basel iii", "basel ii", "dodd-frank", "solvency ii", "stress test", "kpi", "financial reporting",
        "aml", "kyc", "fatca", "miFID", "esg reporting",

        # Tax & treasury
        "tax liability", "deferred tax", "tax shield", "effective tax rate", "transfer pricing", "withholding tax", "treasury management",

        # Macroeconomics & policy
        "inflation", "deflation", "interest rates", "monetary policy", "fiscal policy", "exchange rate", "foreign direct investment", "gdp", "cpi", "ppi",

        # Corporate actions
        "mergers", "acquisitions", "m&a", "spin-off", "buyback", "stock split", "tender offer", "leveraged buyout", "lbo", "management buyout", "mbo",

        # Alternative finance & fintech
        "crowdfunding", "peer-to-peer lending", "blockchain", "cryptocurrency", "tokenization", "smart contract", "defi", "digital wallet",
    ]

    text_lower = text.lower()
    for kw in financial_keywords:
        if kw in text_lower:
            print(f"✅ Found financial keyword: {kw}")  # Debug log
            return True, kw   # Return both True and the matched keyword
    return False, None

    # return any(kw in text_lower for kw in financial_keywords)


def extract_text_from_file(file_path,file_bytes):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        pdf = Paraphrasepdf()
        text=pdf.extract_text_from_pdf(file_bytes)
        return text, "pdf"

    elif ext in [".xls", ".xlsx"]:
        ex = ExcelDataProcessor()
        text = ex.extract_text_from_excel(file_path)
        return text, "excel"

    elif ext in [".doc", ".docx"]:
        doc = DocumentParaphraser()
        text = doc.extract_text_from_docx(file_bytes)
        return text, "docx"

    else:
        return "", "unknown"

