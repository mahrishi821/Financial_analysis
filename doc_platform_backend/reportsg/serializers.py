from rest_framework import serializers
from .models import UserFile, ExtractedData

class UserFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFile
        fields = "__all__"

class ExtractedDataSerializer(serializers.ModelSerializer):
    class Meta:
        model=ExtractedData
        fields="__all__"
