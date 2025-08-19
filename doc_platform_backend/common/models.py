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
    created_at=models.DateTimeField(default=datetime.now)
    updated_at=models.DateTimeField(auto_now=True)
    deleted_at=models.DateTimeField(null=True)
    deleted=models.BooleanField(default=False)
    # auth_id=
    email=models.EmailField(max_length=225,unique=True,db_index=True)
    name=models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects=UserManager()

    USERNAME_FIELD='email'

    def __str__(self):
        return self.email
    def delete(self, *args,**kwargs):
        """soft delete"""
        self.deleted=True
        self.deleted_at=datetime.now()
        self.save(update_fields=['deleted','deleted_at'])
    def hard_delete(self,*args,**kwargs):
        """permanent delete"""
        super(User,self).delete(*args,**kwargs)


