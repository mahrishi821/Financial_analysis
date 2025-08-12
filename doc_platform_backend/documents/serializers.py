from rest_framework import serializers
from .models import DocumentUpload , ExtractedDocument


class ExtractedDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtractedDocument
        fields = ['id', 'file_name', 'file_path', 'file_type', 'preview_text']

class DocumentUploadSerializer(serializers.ModelSerializer):
    extracted_files = ExtractedDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = DocumentUpload
        fields = ['id', 'company', 'zip_file', 'upload_date', 'uploaded_by', 'file_size', 'extracted_files']
        read_only_fields = ['upload_date', 'file_size']

    def create(self, validated_data):
        zip_file = validated_data['zip_file']
        validated_data['file_size'] = zip_file.size
        return super().create(validated_data)



