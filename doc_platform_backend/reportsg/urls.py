from django.urls import path
# from .views import FileUploadView, GenerateReportView
from .views import FileUploadView, GeneratedReportListView

urlpatterns = [
    path("upload/", FileUploadView.as_view(), name="file-upload"),
    path('files/', GeneratedReportListView.as_view(), name='userfile-list'),
]
