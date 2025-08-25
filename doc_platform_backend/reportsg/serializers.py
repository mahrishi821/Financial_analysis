from rest_framework import serializers
from .models import UserFile, ExtractedData, GeneratedInsight
from rest_framework import serializers
from pathlib import Path
from .models import UserFile, GeneratedInsight, Visualization, GeneratedReports
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
        fields = ['raw_file', 'report_file', 'created_at']
        read_only_fields = ['created_at']

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        if instance.report_file:
            rep['raw_file'] = {
                "id": instance.raw_file.id,
                "file_name": instance.raw_file.file_name,
                "created_at": instance.raw_file.created_at,
            }

        return rep


