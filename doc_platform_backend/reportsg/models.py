from django.db import models

class UserFile(models.Model):
    STATUS_CHOICES = [
        ("uploaded", "Uploaded"),
        ("processing", "Processing"),
        ("declined", "Declined"),
        ("error", "Error"),
        ("done", "Done"),
    ]
    file = models.FileField(upload_to="uploads/",null=True)
    file_type = models.CharField(max_length=255)
    file_name = models.CharField(max_length=255)
    extracted_text = models.TextField(blank=True, null=True)
    is_valid = models.BooleanField(default=False)
    validation_reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="uploaded")
    created_at = models.DateTimeField(auto_now_add=True)


class ExtractedData(models.Model):
    file = models.OneToOneField(UserFile, on_delete=models.CASCADE,related_name="extracted_data")
    raw_text = models.TextField()
    tables = models.JSONField(blank=True, null=True)
    structured_sections = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class GeneratedInsight(models.Model):
    file = models.OneToOneField(
        "UserFile",
        on_delete=models.CASCADE,
        related_name="generated_insight"
    )
    summary = models.TextField()
    insights = models.JSONField()  # { trends: [], anomalies: [], kpis: {} }
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Insights for {self.file.file_name}"

class Visualization(models.Model):

    file = models.ForeignKey(UserFile, on_delete=models.CASCADE, related_name="visualizations")
    insight = models.ForeignKey(GeneratedInsight, on_delete=models.CASCADE, related_name="visualizations", null=True, blank=True)
    chart_type = models.CharField(max_length=50)      # line, bar, pie
    title = models.CharField(max_length=255)
    config = models.JSONField(default=dict)           # stores x/y/labels/provenance
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.chart_type}: {self.title}"
