from rest_framework import serializers
from .models import UploadedFile

class UploadFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = ("file_id", "filename", "s3_path", "uploaded_at")
        read_only_fields = ("file_id","uploaded_at")
