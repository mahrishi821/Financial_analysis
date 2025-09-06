# classifier/tasks.py
# from celery import shared_task
from ..models import SheetUnit, AuditLog
import re

RULE_KEYWORDS = {
    "cap_table": ["shareholder", "shares", "ownership", "%", "class", "option", "vesting"],
    "balance_sheet": ["assets", "liabilities", "equity", "total assets", "total liabilities", "net assets"],
    "pnl": ["revenue", "net income", "profit", "gross profit", "operating expense", "cost of goods"],
    "cash_flow": ["cash flow", "net cash", "operating activities", "investing", "financing"],
}

def rule_based_classify(header_rows, sample_rows,pre_header_context):
    text = " ".join([" ".join(r).lower() for r in (header_rows + sample_rows)])
    scores = {}
    for k, keywords in RULE_KEYWORDS.items():
        score = sum(text.count(w) for w in keywords)
        scores[k] = score
    top = max(scores, key=scores.get)
    if scores[top] == 0:
        return None, 0.0
    # normalize confidence
    total = sum(scores.values())
    return top, scores[top] / (total + 1e-9)

# @shared_task
def task_classify_sheet(sheet_unit_id):
    sheet = SheetUnit.objects.get(id=sheet_unit_id)
    label, conf = rule_based_classify(sheet.header_rows or [], sheet.sample_rows or [])
    if label:
        sheet.classification = label
        sheet.classification_confidence = float(conf)
        sheet.save()
        AuditLog.objects.create(sheet_unit=sheet, action="classified_rule", details={"label": label, "confidence": conf})
    # else:
    #     # fallback to LLM (pseudocode)
    #     # create prompt using headers + samples and ask label + confidence
    #     # call llm_client.classify(...)
    #     llm_label = "unknown"  # replace with real LLM call
    #     llm_conf = 0.6
    #     sheet.classification = llm_label
    #     sheet.classification_confidence = llm_conf
    #     sheet.save()
    #     AuditLog.objects.create(sheet_unit=sheet, action="classified_llm", details={"label": llm_label, "confidence": llm_conf})

    # # enqueue processing
    # from ..chunker.tasks import task_process_sheet
    # task_process_sheet(sheet.id)
    return "hehe"

