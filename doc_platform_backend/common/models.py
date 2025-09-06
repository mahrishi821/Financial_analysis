from django.db import models
import uuid
from datetime import  datetime, date, timedelta
from django.utils import timezone
from django.contrib.auth.models import(
    AbstractUser,
    BaseUserManager,
    PermissionsMixin,
    Permission,
    Group,
    AbstractBaseUser
)
from django.core.validators import RegexValidator
from django.db import models
from .enums.company_enums import Sector, SubSector
from datetime import datetime, date, timedelta
import mimetypes
import datetime
# Create your models here.

class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User."""
        if not email:
            raise ValueError("The Email field must be set")
        user=self.model(email=self.normalize_email(email),**extra_fields)
        user.set_password(password)  # Hash password
        user.save(using=self._db)
        return user

    def create_superuser(self,email,password=None,**extra_fields):
        """Create and save a SuperUser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email,password,**extra_fields)
    def get_queryset(self):
        """ overiding default queryset for excluding deleted user """
        return super().get_queryset().filter(deleted=False)
    def all_with_deleted(self):
        """ optional::  for get all the user even which are deleted also"""
        return super().get_queryset()
class User(AbstractBaseUser,PermissionsMixin):
    """ users"""
    unique_id=models.UUIDField(unique=True,default=uuid.uuid4,editable=False)
    created_at=models.DateTimeField(default=timezone.now)
    updated_at=models.DateTimeField(auto_now=True)
    deleted_at=models.DateTimeField(null=True)
    deleted=models.BooleanField(default=False)
    email=models.EmailField(max_length=225,unique=True,db_index=True)
    name=models.CharField(max_length=255)
    dob=models.DateField(null=True,blank=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True,null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects=UserManager()

    USERNAME_FIELD='email'

    def __str__(self):
        return self.email
    def delete(self, *args,**kwargs):
        """soft delete"""
        self.deleted=True
        self.deleted_at=timezone.now()
        self.save(update_fields=['deleted','deleted_at'])
    def hard_delete(self,*args,**kwargs):
        """permanent delete"""
        super(User,self).delete(*args,**kwargs)

class BaseModelManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted=False)


class BaseModel(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def delete(self):
        self.deleted_at = datetime.now()
        self.deleted = True
        self.save()


class ModelManager(BaseModel):
    class Meta:
        abstract = True

    objects = BaseModelManager()
class Company(ModelManager):
    FREQUENCY_CHOICES = [
        ('Quarterly', 'Quarterly'),
        ('Semi-Annual', 'Semi-Annual'),
        ('Annual', 'Annual'),
    ]

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Offboarded', 'Offboarded'),
    ]

    company_name = models.CharField(max_length=255, unique=True)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name='created_by',null=True)
    sector = models.CharField(max_length=50, choices=Sector.choices)
    sub_sector = models.CharField(max_length=50, choices=SubSector.choices, blank=True)
    country = models.CharField(max_length=100)
    incorporation_date = models.DateField()
    contact_person_name = models.CharField(max_length=100)
    contact_email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')



    def __str__(self):
        return self.company_name

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

class UserFile(models.Model):
    STATUS_CHOICES = [
        ("uploaded", "Uploaded"),
        ("processing", "Processing"),
        ("declined", "Declined"),
        ("error", "Error"),
        ("done", "Done"),
    ]
    created_by = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
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

class GeneratedReports(models.Model):
    raw_file=models.ForeignKey(UserFile,on_delete=models.CASCADE,related_name='uploaded_file')
    created_at=models.DateTimeField(auto_now_add=True)
    file_name=models.CharField(max_length=200,null=True)
    report_file=models.FileField(upload_to="reports/",null=True,blank=True)

    def __str__(self):
        return f"report_file"

class AssetAnalysis(models.Model):

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="asset_analysis",null=True)
    asset_query=models.CharField(max_length=500)
    query_datetime=models.DateTimeField(default=timezone.now)

    class Meta:
        db_table='asset_analysis'
    def __str__(self):

        return f"{self.asset_query}"

class ChatbotUpload(models.Model):
    file = models.FileField(upload_to="chatbot_docs/")
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name="uploaded_user",null=True)
    processed = models.BooleanField(default=False)

    def __str__(self):
        return f"ChatbotDoc: {self.file_name}"


class ChatbotChunk(models.Model):
    upload = models.ForeignKey(ChatbotUpload, on_delete=models.CASCADE, related_name="chunks",null=True)
    chunk_text = models.TextField()
    vector_id = models.CharField(max_length=255, null=True, blank=True)  # Pinecone ID
    created_at = models.DateTimeField(auto_now_add=True)


class ChatbotSession(models.Model):

    upload = models.ForeignKey(ChatbotUpload, on_delete=models.CASCADE, related_name="sessions")
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
