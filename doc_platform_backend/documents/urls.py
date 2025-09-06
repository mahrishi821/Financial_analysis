from rest_framework.routers import DefaultRouter
# from .views import (DocumentUploadViewSet, ParaphrasePDFView, ParaphraseDOCXView ,ParaphraseExcelView, DocumentUploadView,FileTextClassificationView)
from .views import UploadZipView
from django.urls import path

router = DefaultRouter()
# router.register(r'document-uploads', DocumentUploadViewSet, basename='document-upload')
urlpatterns = [
    # path('paraphrase-pdf/', ParaphrasePDFView.as_view(), name='paraphrase-pdf'),
    # path('paraphrase-doc/', ParaphraseDOCXView.as_view(), name='paraphrase-doc'),
    # path('paraphrase-excel/', ParaphraseExcelView.as_view(), name='paraphrase-excel'),
    # path('upload-zip/', DocumentUploadView.as_view(), name='upload-zip'),
    # path('filetype/', FileTextClassificationView.as_view(), name='filetype'),
    path('upload_file/', UploadZipView.as_view(),name='upload_file'),
]
urlpatterns += router.urls
