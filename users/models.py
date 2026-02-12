import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

from tenants.mixins import TenantUserMixin

# Create your models here.
class User(AbstractUser, TenantUserMixin):
    id =  models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    # ---  CONFIG ---
    # Tell Django to use Email instead of Username for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username'] # 'email' is already required by USERNAME_FIELD
    # -------------------


    class Meta:
        db_table = "auth_user"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email