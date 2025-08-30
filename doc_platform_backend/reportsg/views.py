import os
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from common.jsonResponse.response import JSONResponseSender
from common.models import UserFile, GeneratedReports, AssetAnalysis
from common.serializers import (
    UserFileSerializer,
    GeneratedReportsSerializer,
    AssetAnalysisSerializer,
    ReportSerializer,
)
from .utils.tasks import preprocess_file_task
from .utils.AssetAnalysis import FinancialAnalysisPipeline


class UserFileListView(ListAPIView):
    queryset = UserFile.objects.all().order_by('-created_at')
    serializer_class = UserFileSerializer
    permission_classes = [IsAuthenticated]  # optional

class FileUploadView(APIView):
    def post(self, request):
        uploaded_file = request.FILES.get("file")
        created_by=request.user
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
                validation_reason="Passed initial validation",
                created_by=created_by,
            )
            response=preprocess_file_task(obj.id)
            obj.refresh_from_db()

            if "Report generated Successfully" in response:
                return JSONResponseSender.send_success(
                {"file_id": obj.id, "status": obj.status, "valid": obj.is_valid, "message":"Report generated Successfully","uploaded_by":obj.created_by.name},
            )
            elif "Not financial" in response:
                return JSONResponseSender.send_error("400","Document not financial","Document not financial")

            else:
                return JSONResponseSender.send_error("400",response.get("error", "Unknown error"),response.get("error", "Unknown error"))

        except Exception as e:
            return JSONResponseSender.send_error("500", str(e), str(e))

class GeneratedReportViewSet(viewsets.ModelViewSet):

    serializer_class = GeneratedReportsSerializer
    def get_queryset(self):

        query_set=GeneratedReports.objects.filter(raw_file__created_by=self.request.user).order_by("-created_at")
        return query_set


    @action(detail=False, methods=['get'])
    def report_count(self,request,*args, **kwargs):
        try:
            report_c=GeneratedReports.objects.filter(raw_file__created_by=self.request.user).count()
            return JSONResponseSender.send_success({"report_count":report_c})
        except Exception as e:
            return JSONResponseSender.send_error("500", str(e), str(e))

class AssetAnalysisViewSet(viewsets.ModelViewSet):
    serializer_class = AssetAnalysisSerializer
    def get_queryset(self):
        queryset = AssetAnalysis.objects.filter(created_by=self.request.user).order_by("query_datetime")
        return queryset

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            analysis = serializer.save()
            asset_query = serializer.validated_data["asset_query"]
            try:
                result = FinancialAnalysisPipeline.run_analysis(asset_query, work_dir=f"./coding/asset_analysis_{analysis.id}")
                if result.get("report"):
                    return JSONResponseSender.send_success({"id": analysis.id,"asset_query": asset_query,"report": result["report"],"figures": result["figures"],"query_datetime": analysis.query_datetime})
                else:
                    return JSONResponseSender.send_error("400","report not found",result)
            except Exception as e:
                return JSONResponseSender.send_error("500",str(e),str(e))

    @action(detail=False, methods=['get'])
    def analysiscount(self,request,*args, **kwargs):
        try:
            analysis = AssetAnalysis.objects.filter(created_by=self.request.user).count()
            return JSONResponseSender.send_success({"asset_count":analysis})
        except Exception as e:
            return JSONResponseSender.send_error("500",str(e),str(e))

