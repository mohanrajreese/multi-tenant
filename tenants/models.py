from uuid import uuid4
from django.db import models
from django.contrib.auth.models import Permission

class Tenant(models.Model):
    """
    The Organization/Client that owns data.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, help_text="Unique name for the tenant (e.g., acme-corp)")
    
    # Subscription/Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name



class Domain(models.Model):
    """
    The URL associated with a tenant.
    """
    STATUS_CHOICES = (
        ('PENDING', 'Pending Verification'),
        ('ACTIVE', 'Active'),
        ('FAILED', 'Verification Failed'),
    )

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    domain = models.CharField(max_length=255, unique=True, db_index=True)
    tenant = models.ForeignKey(Tenant, related_name='domains', on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=False)
    is_custom = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.domain} ({self.tenant.name})"



class TenantQuerySet(models.QuerySet):
    def for_tenant(self, tenant):
        return self.filter(tenant=tenant)



class TenantManager(models.Manager):
    def get_queryset(self):
        from .utils import get_current_tenant
        tenant = get_current_tenant()
        
        # We start with the base queryset
        queryset = TenantQuerySet(self.model, using=self._db)
        
        # If a tenant is identified in the request, we filter automatically
        if tenant:
            return queryset.filter(tenant=tenant)
            
        # If no tenant (e.g., Public view or Management Command), return all
        return queryset



class TenantAwareModel(models.Model):
    """
    Abstract base model that automatically scopes queries to the current tenant.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='%(class)ss')
    # The 'objects' manager is now tenant-aware!
    objects = TenantManager()
    
    # We keep a 'plain' manager for when we EXPLICITLY need all data (e.g. Admin)
    unscoped_objects = models.Manager()
    class Meta:
        abstract = True
    def save(self, *args, **kwargs):
        if not self.tenant_id:
            from .utils import get_current_tenant
            current_tenant = get_current_tenant()
            if current_tenant:
                self.tenant = current_tenant
        super().save(*args, **kwargs)







class Role(TenantAwareModel):
    """
    A collection of permissions scoped to a tenant.
    Example: 'Manager' for 'Acme Corp'.
    """
    name = models.CharField(max_length=50)
    permissions = models.ManyToManyField(Permission, blank=True)

    class Meta:
        unique_together = ('tenant', 'name')

    def __str__(self):
        return f"{self.name} ({self.tenant.name})"

class Membership(models.Model):
    """
    The final link. User <-> Tenant <-> Role.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='memberships')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='memberships')
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'tenant')

    def __str__(self):
        return f"{self.user.email} is {self.role.name} at {self.tenant.name}"

class TenantInvitation(TenantAwareModel):
    """
    A pending invitation for a user to join a tenant.
    """
    email = models.EmailField()
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid4, unique=True, editable=False)
    invited_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='sent_invitations')
    
    is_accepted = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"Invite for {self.email} to {self.tenant.name}"

class AuditLog(TenantAwareModel):
    """
    Complete end-to-end tracking of all changes.
    """
    ACTION_CHOICES = (
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
    )

    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=255) # String to handle UUID or Int
    object_repr = models.CharField(max_length=255) # string representation of object
    
    # Store changes as JSON: {"field_name": [old_value, new_value]}
    changes = models.JSONField(default=dict, blank=True)
    
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.action} on {self.model_name} by {self.user}"