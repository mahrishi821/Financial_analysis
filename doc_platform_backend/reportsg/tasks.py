# app/tasks.py
from celery import shared_task
from .models import UserFile, ExtractedData
from .utils import extract_text_from_file, is_financial_text
from common.third_party_integration.excel_pharaphraser import ExcelDataProcessor
import os
import pandas as pd

def dataframe_to_json_serializable(df: pd.DataFrame):
    def convert_value(x):
        # Handle missing
        if pd.isna(x):
            return None
        # Handle timestamps/dates
        if hasattr(x, "isoformat"):
            return x.isoformat()
        # Pass-through primitive JSON types
        if isinstance(x, (int, float, bool, type(None))):
            return x
        # Fallback → string
        return str(x)

    return df.applymap(convert_value).to_dict(orient="records")



@shared_task
def preprocess_file_task(file_id):
    try:
        user_file = UserFile.objects.get(id=file_id)
        user_file.status = "processing"
        user_file.save()

        # Read file bytes
        file_path = user_file.file.path  # adjust if stored differently
        with open(file_path, "rb") as f:
            file_bytes = f.read()

        # Extract text + type
        text, file_type = extract_text_from_file(file_path, file_bytes)

        tables_json = None
        # Handle Excel separately with structured extraction
        if file_type == "excel":
            try:
                xl = pd.ExcelFile(file_path)
                tables_json = {
                    sheet: dataframe_to_json_serializable(xl.parse(sheet))
                    for sheet in xl.sheet_names
                }
            except Exception:
                tables_json = None

        # Financial check
        if not is_financial_text(text):
            user_file.is_valid = False
            user_file.validation_reason = "Document not financial"
            user_file.save()
            return {"status": "invalid", "reason": "Not financial"}

        # Very basic section tagging (can be expanded later)
        sections = {"narrative": text[:1000]}  # placeholder

        # Save structured data
        ExtractedData.objects.create(
            file=user_file,
            raw_text=text,
            tables=tables_json,
            structured_sections=sections
        )

        user_file.is_valid = True
        user_file.validation_reason = "Financial document detected"
        user_file.status = "done"
        user_file.save()

        return {"status": "success", "file_id": file_id}

    except Exception as e:
        user_file.status = "error"
        user_file.validation_reason = str(e)
        user_file.save()
        return {"status": "error", "error": str(e)}
