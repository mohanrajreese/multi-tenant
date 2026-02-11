import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
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



    def has_tenant_permission(self, tenant, perm_codename):
        """
        Enterprise-grade permission check.
        Checks if the user has a specific permission within a specific tenant context.
        """
        # 1. Get the user's membership for this tenant
        membership = self.memberships.filter(tenant=tenant, is_active=True).select_related('role').first()
        
        if not membership or not membership.role:
            return False
            
        # 2. Check if the role has the permission
        # A permission codename looks like 'view_product' or 'add_user'
        return membership.role.permissions.filter(codename=perm_codename).exists()