import os
import tempfile
from django.template.loader import render_to_string
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from common.jsonResponse.response import JSONResponseSender
from common.models import UserFile, GeneratedReports, AssetAnalysis
from common.serializers import (
    UserFileSerializer,
    GeneratedReportsSerializer,
    AssetAnalysisSerializer,
    ReportSerializer,
)
from .utils import extract_text_from_file
from .tasks import preprocess_file_task
from .AssetAnalysisAi import run_asset_analysis

class UserFileListView(ListAPIView):
    queryset = UserFile.objects.all().order_by('-created_at')
    serializer_class = UserFileSerializer
    permission_classes = [IsAuthenticated]  # optional

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

            if "Report generated Successfully" in response:
                return JSONResponseSender.send_success(
                {"file_id": obj.id, "status": obj.status, "valid": obj.is_valid, "message":"Report generated Successfully"},
            )
            else:
                return JSONResponseSender.send_error("400",response.get("error", "Unknown error"),response.get("error", "Unknown error"))

        except Exception as e:
            return JSONResponseSender.send_error("500", str(e), str(e))
class GeneratedReportListView(ListAPIView):
    queryset = GeneratedReports.objects.all().order_by("-created_at")
    serializer_class = GeneratedReportsSerializer

class AssetAnalysisView(APIView):
    def post(self, request):
        serializer = AssetAnalysisSerializer(data=request.data)
        if serializer.is_valid():
            analysis = serializer.save()
            asset_query = serializer.validated_data["asset_query"]
            try:
                result = run_asset_analysis(asset_query, work_dir=f"./coding/asset_analysis_{analysis.id}")
                if result.get("report"):
                    return JSONResponseSender.send_success({"id": analysis.id,"asset_query": asset_query,"report": result["report"],"figures": result["figures"],"query_datetime": analysis.query_datetime})
                else:
                    return JSONResponseSender.send_error("400","report not found",result)
            except Exception as e:
                return JSONResponseSender.send_error("500",str(e),str(e))