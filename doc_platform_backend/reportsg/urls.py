from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import FileUploadView, GeneratedReportViewSet,AssetAnalysisViewSet

router = DefaultRouter()
router.register(r'reports', GeneratedReportViewSet, basename='reports')
router.register(r'assets', AssetAnalysisViewSet, basename='assets')

# api/assets/analysiscount/   assets count endpoint

urlpatterns = [
    path("upload/", FileUploadView.as_view(), name="file-upload"),
]

urlpatterns+=router.urls