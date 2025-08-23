from rest_framework import serializers
from .models import UserFile, ExtractedData, GeneratedInsight

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
