from rest_framework.routers import DefaultRouter
from .views import DocumentUploadViewSet, ParaphrasePDFView, ParaphraseDOCXView ,ParaphraseExcelView, DocumentUploadView
from django.urls import path

router = DefaultRouter()
router.register(r'document-uploads', DocumentUploadViewSet, basename='document-upload')
urlpatterns = [
    path('paraphrase-pdf/', ParaphrasePDFView.as_view(), name='paraphrase-pdf'),
    path('paraphrase-doc/', ParaphraseDOCXView.as_view(), name='paraphrase-doc'),
    path('paraphrase-excel/', ParaphraseExcelView.as_view(), name='paraphrase-excel'),
    path('upload-zip/', DocumentUploadView.as_view(), name='upload-zip'),
]
urlpatterns += router.urls
