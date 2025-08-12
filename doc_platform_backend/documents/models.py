from django.db import models
from companies.models import Company
import mimetypes

from datetime import datetime

def upload_to_zip(instance, filename):
    today = datetime.today().strftime("%Y_%m_%d")
    return f"uploads/{instance.company.id}/{today}/{filename}"


class DocumentUpload(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="uploads")
    zip_file = models.FileField(upload_to=upload_to_zip)
    upload_date = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.CharField(max_length=100, blank=True)  # optionally set from request user
    file_size = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.company.company_name} - {self.zip_file.name}"


class ExtractedDocument(models.Model):
    upload = models.ForeignKey(DocumentUpload, on_delete=models.CASCADE, related_name='extracted_files')
    file_name = models.CharField(max_length=255)
    file_path = models.TextField()
    file_type = models.CharField(max_length=50)
    preview_text = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.file_type:
            self.file_type = mimetypes.guess_type(self.file_path)[0] or 'unknown'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.file_name} ({self.file_type})"
