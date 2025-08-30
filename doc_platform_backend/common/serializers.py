from rest_framework import serializers
from .models import (User, Company, DocumentUpload , ExtractedDocument, GeneratedReports, AssetAnalysis,UserFile,

                     ExtractedData, GeneratedInsight,ChatbotUpload,ChatbotSession)
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from pathlib import Path

class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'name', 'password', 'confirm_password']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(email=attrs['email'], password=attrs['password'])
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled")
        attrs['user'] = user
        return attrs

    def create_tokens(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


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



class UserFileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserFile
        fields = "__all__"

class ExtractedDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtractedData
        fields = "__all__"

class GeneratedInsightSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedInsight
        fields = ["id", "file", "summary", "insights", "created_at"]




class ReportSerializer(serializers.ModelSerializer):
    pdf_link = serializers.SerializerMethodField()
    # summary = serializers.SerializerMethodField()
    # insights = serializers.SerializerMethodField()
    # charts = serializers.SerializerMethodField()

    class Meta:
        model = UserFile
        fields = ['id', 'file_name', 'status', 'is_valid', 'created_at', 'pdf_link']

    def get_pdf_link(self, obj):
        # assuming report is saved as media/reports/report_<id>.pdf
        report_path = f"/media/reports/report_{obj.id}.pdf"
        if obj.status == "done" and Path(f"media/reports/report_{obj.id}.pdf").exists():
            return report_path
        return None

    # def get_summary(self, obj):
    #     insight = GeneratedInsight.objects.filter(file=obj).first()
    #     return insight.summary if insight else None
    #
    # def get_insights(self, obj):
    #     insight = GeneratedInsight.objects.filter(file=obj).first()
    #     return insight.insights if insight else None
    #
    # def get_charts(self, obj):
    #     charts = Visualization.objects.filter(file=obj)
    #     return [chart.config for chart in charts]
    #
class GeneratedReportsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedReports
        fields = ['report_file', 'created_at']
        read_only_fields = ['created_at']




class AssetAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetAnalysis
        fields = '__all__'
        read_only_fields = ["query_datetime"]


class ChatbotUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatbotUpload
        fields = ["id", "file", "file_name", "file_type", "uploaded_at", "processed","uploaded_by"]

class ChatbotSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatbotSession
        fields = ["id", "upload", "question", "answer", "created_at"]
