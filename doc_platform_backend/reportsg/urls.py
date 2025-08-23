from django.urls import path
# from .views import FileUploadView, GenerateReportView
from .views import FileUploadView, PreprocessFileView, FileStatusView

urlpatterns = [
    path("upload/", FileUploadView.as_view(), name="file-upload"),
    # path("report/<int:file_id>/", GenerateReportView.as_view(), name="generate-report"),
    path("files/<int:file_id>/preprocess/", PreprocessFileView.as_view(), name="file-preprocess"),
    path("files/<int:pk>/status/", FileStatusView.as_view(), name="file-status"),
]
