from django.urls import path
# from .views import FileUploadView, GenerateReportView
from .views import FileUploadView, GeneratedReportListView, GeneratedReports, AssetAnalysisView

urlpatterns = [
    path("upload/", FileUploadView.as_view(), name="file-upload"),
    path('files/', GeneratedReportListView.as_view(), name='userfile-list'),
    path("asset-analysis/", AssetAnalysisView.as_view(), name="asset-analysis"),
    # path('report/',GeneratedReports.as_view(),name='generatereport')
]
