from django.db import models
from .enums.company_enums import Sector, SubSector
from datetime import datetime, date, timedelta

class BaseModelManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted=False)


class BaseModel(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    created_at = models.DateTimeField(default=datetime.now)
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
