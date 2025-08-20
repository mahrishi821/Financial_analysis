import tempfile, os
from rest_framework.views import APIView
from .utils import extract_text_from_file
from rest_framework.views import APIView
from common.jsonResponse.response import JSONResponseSender
from django.template.loader import render_to_string
from .models import UserFile
from django.http import HttpResponse
from common.ai.orchestrator import FinanceReportOrchestrator

# Optional: PDF export (WeasyPrint)
try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except Exception:
    WEASYPRINT_AVAILABLE = False

class FileUploadView(APIView):
    def post(self, request):
        uploaded_file = request.FILES.get('file')

        if not uploaded_file:
            return JSONResponseSender.send_error("400", "No file provided", "No file provided")
        ext = os.path.splitext(uploaded_file.name)[1].lower()
        if ext not in  [".pdf",".xls", ".xlsx",".doc", ".docx"] :
            return JSONResponseSender.send_error("400", "Unsupported file type", "support only excel, docs and pdf ")
        try:

            suffix = os.path.splitext(uploaded_file.name)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                for chunk in uploaded_file.chunks():
                    tmp.write(chunk)
                tmp_path = tmp.name


            with open(tmp_path, "rb") as f:
                file_bytes = f.read()


            text, file_type = extract_text_from_file(tmp_path, file_bytes)


            obj = UserFile()
            obj.file_name = uploaded_file.name
            obj.file_type = file_type
            obj.extracted_text = text
            obj.save()

            os.remove(tmp_path)

            return JSONResponseSender.send_success(text)

        except Exception as e:
            return JSONResponseSender.send_error("500", str(e), str(e))
#
#
#
# class GenerateReportView(APIView):
#     def get(self, request, file_id):
#         try:
#             obj = UserFile.objects.get(id=file_id)
#
#             # Step 1: Extracted text from DB
#             extracted_text = obj.extracted_text
#
#             # Step 2: Generate AI report
#             ai = AgenticAI()
#             ai_summary = ai.generate_report(extracted_text)
#
#             # # Step 3: Render HTML report
#             # context = {
#             #     "file_name": obj.file_name,
#             #     "file_type": obj.file_type,
#             #     "summary": ai_summary,
#             #     "raw_text": extracted_text  # optional, can be hidden later
#             # }
#             # html_report = render_to_string("report_template.html", context)
#
#             return JSONResponseSender.send_success(ai_summary)
#             # return JSONResponseSender.send_success({"report_html": html_report})
#
#         except UserFile.DoesNotExist:
#             return JSONResponseSender.send_error("404", "File not found", "Invalid file_id")
#         except Exception as e:
#             return JSONResponseSender.send_error("500", str(e), str(e))


class GenerateReportView(APIView):
    """
    GET /api/report/<file_id>/?format=html|pdf
    - Returns polished HTML by default
    - If ?format=pdf and WeasyPrint available, returns a PDF download
    """
    def get(self, request, file_id):
        fmt = request.GET.get("format", "html").lower()
        print(f"fmt = {fmt}")
        try:
            obj = UserFile.objects.get(id=file_id)
            orchestrator = FinanceReportOrchestrator(model="openai/gpt-4o-mini")
            html = orchestrator.run(
                file_name=obj.file_name,
                file_type=obj.file_type,
                extracted_text=obj.extracted_text
            )

            if fmt == "pdf":
                if not WEASYPRINT_AVAILABLE:
                    return JSONResponseSender.send_error("400", "PDF not available", "Install WeasyPrint first")
                pdf_bytes = HTML(string=html).write_pdf()
                resp = HttpResponse(pdf_bytes, content_type="application/pdf")
                resp["Content-Disposition"] = f'attachment; filename="report_{file_id}.pdf"'
                return JSONResponseSender.send_success(resp)

            # default HTML (pure HTML response, not JSON, so no escaping)
            return JSONResponseSender.send_success(html)

        except UserFile.DoesNotExist:
            return JSONResponseSender.send_error("404", "File not found", "Invalid file_id")
        except Exception as e:
            return JSONResponseSender.send_error("500", str(e), str(e))
