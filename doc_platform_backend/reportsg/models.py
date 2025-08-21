from django.db import models

class UserFile(models.Model):
    file=models.FileField(upload_to="uploads/",null=True)
    file_type = models.CharField(max_length=255)
    file_name = models.CharField(max_length=255)
    extracted_text = models.TextField(blank=True, null=True)
    is_valid=models.BooleanField(default=False)
    validation_reason=models.TextField(blank=True,null=True)
    status=models.CharField(max_length=50,default="uploaded")
    created_at = models.DateTimeField(auto_now_add=True)


class ExtractedData(models.Model):
    file=models.OneToOneField(UserFile,on_delete=models.CASCADE,related_name="extracted_data")
    raw_text=models.TextField()
    tables=models.JSONField(blank=True,null=True)
    structured_sections=models.JSONField(blank=True,null=True)
    created_at=models.DateTimeField(auto_now=True)

