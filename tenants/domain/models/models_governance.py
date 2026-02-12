from django.db import models
from .base import TenantAwareModel

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
    impersonator = models.ForeignKey(
        'users.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='impersonated_logs',
        help_text="The staff member who performed this action while acting as the user."
    )
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=255)
    object_repr = models.CharField(max_length=255)
    changes = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.action} on {self.model_name} by {self.user}"

class Quota(TenantAwareModel):
    """
    Usage limits for a tenant.
    """
    resource_name = models.CharField(max_length=50)
    limit_value = models.IntegerField(default=0)
    current_usage = models.IntegerField(default=0)

    class Meta:
        unique_together = ('tenant', 'resource_name')

    def __str__(self):
        return f"{self.resource_name} limit for {self.tenant.name}"
