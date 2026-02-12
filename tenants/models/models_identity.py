from uuid import uuid4
from django.db import models
from django.contrib.auth.models import Permission
from .base import TenantAwareModel

class Role(TenantAwareModel):
    """
    A collection of permissions scoped to a tenant.
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
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='memberships')
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
