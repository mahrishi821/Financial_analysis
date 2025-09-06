from  common.models import User
from django.db import models
from django.contrib.postgres.indexes import GinIndex
from django.db.models import  JSONField
from django.conf import settings
import uuid
from django.db import models


class UploadedFile(models.Model):
    file_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    filename = models.CharField(max_length=512)
    s3_path = models.FileField(upload_to="UploadedFile/",null=True,blank=True)   # or use Django Storage's FileField
    uploaded_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(null=True, blank=True)

class SheetUnit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uploaded_file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE, related_name='sheets')
    sheet_name = models.CharField(max_length=255)
    row_count = models.IntegerField()
    col_count = models.IntegerField()
    header_rows = models.JSONField(null=True)  # normalized header rows as list
    sample_rows = models.JSONField(null=True)  # first N rows used for classification
    raw_table = models.JSONField(null=True)    # full sheet (if bounded size) or pointer to csv in S3
    # status = models.CharField(max_length=50, default='pending')  # pending, classified, mapped, annexed
    metadata = models.JSONField(null=True, blank=True)
    bounding_box = models.JSONField(null=True,blank=True)
    table_index=models.IntegerField(null=True,blank=True)
    classification = models.CharField(max_length=128, null=True)
    classification_confidence = models.FloatField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class StructuredDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sheet_unit = models.OneToOneField(SheetUnit, on_delete=models.CASCADE, related_name='structured')
    schema_type = models.CharField(max_length=128)  # e.g., cap_table, balance_sheet
    json_data = JSONField()                         # final mapped JSON
    provenance = JSONField(null=True)              # original file/sheet positions & chunk metadata
    created_at = models.DateTimeField(auto_now_add=True)

class Annexure(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sheet_unit = models.ForeignKey(SheetUnit, on_delete=models.CASCADE)
    json_data = JSONField()
    reason = models.TextField(null=True)  # why annexure: "unknown format" etc.
    created_at = models.DateTimeField(auto_now_add=True)

class AuditLog(models.Model):
    id = models.AutoField(primary_key=True)
    sheet_unit = models.ForeignKey(SheetUnit, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=128)
    details = JSONField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
