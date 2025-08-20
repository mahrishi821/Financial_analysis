from django.db import models

class UserFile(models.Model):
    file_type = models.CharField(max_length=255)  # pdf, excel, docx
    file_name = models.CharField(max_length=255)
    extracted_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # def __str__(self):
    #     return f"UserFile"
