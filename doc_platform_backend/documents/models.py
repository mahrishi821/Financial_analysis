from django.db import models
from companies.models import Company
import mimetypes
from common.models import User
from datetime import  datetime

from datetime import datetime

def upload_to_zip(instance, filename):
    """Organizing uploads by the company + date for tracebuility"""
    today = datetime.today().strftime("%Y_%m_%d")
    return f"bronze/{instance.company.id}/{today}/{filename}"


class DocumentUpload(models.Model):
    STATUS_CHOICES=[
        ("raw","RAW"),
        ("extracted","EXTRACTED"),
        ("processed","PROCESSED"),
        ("failed","FAILED"),
    ]
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="uploads")
    zip_file = models.FileField(upload_to=upload_to_zip)
    upload_date = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name="uploaded_by")
    status=models.CharField(max_length=20,choices=STATUS_CHOICES,default="raw")
    error_log=models.TextField(blank=True,null=True)
    version=models.IntegerField(default=1)
    file_size = models.PositiveIntegerField()
    #optional fields

    original_filename=models.CharField(max_length=255,null=True,blank=True)
    content_type=models.CharField(max_length=200,blank=True,null=True)

    class Meta:
        db_table="document_uploads"
        indexes=[
            models.Index(fields=["company","upload_date"]),
        ]
        ordering=["-upload_date"]

    def __str__(self):
        return f"{self.company.company_name} - {self.zip_file.name} (v{self.version}"


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
