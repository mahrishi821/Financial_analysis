import tempfile, os
from rest_framework.views import APIView
from .utils import extract_text_from_file
from rest_framework.views import APIView
from django.template.loader import render_to_string
from django.http import HttpResponse
from rest_framework.generics import RetrieveAPIView
from .serializers import UserFileSerializer
import os, tempfile
from rest_framework.views import APIView
from common.jsonResponse.response import JSONResponseSender
from .models import UserFile
from rest_framework.views import APIView
from rest_framework.response import Response
from .tasks import preprocess_file_task
class FileUploadView(APIView):
    def post(self, request):
        uploaded_file = request.FILES.get("file")

        if not uploaded_file:
            return JSONResponseSender.send_error("400", "No file provided", "No file provided")

        ext = os.path.splitext(uploaded_file.name)[1].lower()
        if ext not in [".pdf", ".xls", ".xlsx", ".doc", ".docx"]:
            return JSONResponseSender.send_error("400", "Unsupported file type", "support only excel, docs and pdf")

        if uploaded_file.size > 3 * 1024 * 1024:
            return JSONResponseSender.send_error("400", "File too large", "Max file size is 3MB")

        try:
            obj = UserFile.objects.create(
                file=uploaded_file,
                file_name=uploaded_file.name,
                file_type=ext.replace(".", ""),
                is_valid=True,
                validation_reason="Passed initial validation"
            )
            response=preprocess_file_task(obj.id)
            print(f"response={response}")
            obj.refresh_from_db()

            if 'pdf_link' in response:
                return JSONResponseSender.send_success(
                {"file_id": obj.id, "status": obj.status, "valid": obj.is_valid, "pdf_link": response['pdf_link']},
            )
            else:
                return JSONResponseSender.send_error("400",response.get("error", "Unknown error"),response.get("error", "Unknown error"))

        except Exception as e:
            return JSONResponseSender.send_error("500", str(e), str(e))

# app/views.py
class PreprocessFileView(APIView):
    def post(self, request, file_id):
        try:
            return JSONResponseSender.send_success(preprocess_file_task(file_id))
        except Exception as e:
            return JSONResponseSender.send_error("500", str(e), str(e))




class FileStatusView(RetrieveAPIView):
    queryset = UserFile.objects.all()
    serializer_class = UserFileSerializer


