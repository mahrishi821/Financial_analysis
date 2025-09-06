from celery import shared_task
from common.models import UserFile, ExtractedData,GeneratedInsight,Visualization,GeneratedReports
from .document_processor import extract_text_from_file, is_financial_text
import pandas as pd
import numpy as np
import json
from ..agents.agent2 import ChartGeneratorAgent
from ..agents.agnet3 import ReportGeneratorAgent
from ..agents.agent1 import FinancialDocumentInterpreter
from pathlib import Path
from django.core.files import File

FDI=FinancialDocumentInterpreter()
CGI=ChartGeneratorAgent()
RGA=ReportGeneratorAgent()
def dataframe_to_json_serializable(df: pd.DataFrame):
    # Replace all NaN/NaT with None
    df = df.replace({np.nan: None})

    def convert_value(x):
        # Handle timestamps/dates
        if hasattr(x, "isoformat"):
            return x.isoformat()
        # Pass-through primitive JSON types
        if isinstance(x, (int, float, bool, type(None))):
            return x
        # Fallback → string
        return str(x)

    # Apply conversion
    records = df.applymap(convert_value).to_dict(orient="records")

    # Final guard: ensure JSON-safe (NaN -> null, Infinity -> error out)
    return json.loads(json.dumps(records, allow_nan=False))

@shared_task
def preprocess_file_task(file_id):
    try:
        user_file = UserFile.objects.get(id=file_id)
        user_file.status = "processing"
        user_file.save()

        # --- existing code for extraction ---
        file_path = user_file.file.path
        with open(file_path, "rb") as f:
            file_bytes = f.read()
        text, file_type = extract_text_from_file(file_path, file_bytes)

        if  is_financial_text(text)==False :

            user_file.is_valid = False
            user_file.status="declined"
            user_file.validation_reason = "Document not financial"
            user_file.save()
            return "Not financial"

        sections = {"narrative": text}

        extracted = ExtractedData.objects.create(
            file=user_file,
            raw_text=text,
            tables={},
            structured_sections=sections
        )

        user_file.is_valid = True
        user_file.validation_reason = "Financial document detected"
        user_file.save()

        summary, insights,tables= FDI.run(text)
        print(f"Summary : {summary} \n  insights: {insights} \n tables : {tables}")

        generated_insight = GeneratedInsight.objects.create(file=user_file, summary=summary, insights=insights)

        # --- Agent 4 (NEW) ---
        charts=[]
        if tables:
            charts = CGI.generate_charts(tables)
            print(f"charts :: {charts}")
            Visualization.objects.filter(file=user_file).delete()
            for cfg in charts:
                Visualization.objects.create(
                    file=user_file,
                    chart_type=cfg["type"],
                    title=cfg["title"],
                    config=cfg,
                )

        user_file.status = "done"
        user_file.save()

        output_dir = Path("media/reports")
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / f"report_{user_file.id}.pdf"
        pdf=RGA.generate_report(summary,insights,charts,output_path=str(output_path))
        GeneratedReports.objects.create(
            raw_file=user_file,
            report_file=f"{output_path}",
            file_name=f"{user_file.file_name}_report.pdf",
        )
        print(f"pdf :{pdf}")

        return "Report generated Successfully"

    except Exception as e:
        user_file.status = "error"
        user_file.validation_reason = str(e)
        user_file.save()
        return {"error": str(e)}
