from django.urls import path
# from .views import FileUploadView, GenerateReportView
from .views import FileUploadView, GeneratedReportListView, GeneratedReports

urlpatterns = [
    path("upload/", FileUploadView.as_view(), name="file-upload"),
    path('files/', GeneratedReportListView.as_view(), name='userfile-list'),
    # path('report/',GeneratedReports.as_view(),name='generatereport')
]
