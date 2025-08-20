from common.third_party_integration.doc_paraphraser import DocumentParaphraser
from common.third_party_integration.pdf_paraphraser import Paraphrasepdf
from common.third_party_integration.excel_pharaphraser import ExcelDataProcessor
import os
import pandas as pd
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

