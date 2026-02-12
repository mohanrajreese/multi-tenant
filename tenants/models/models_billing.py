from django.db import models
from .base import TenantAwareModel

class Entitlement(TenantAwareModel):
    """
    Omega Tier: Enterprise Feature Gating.
    Maps specific functional 'Capabilities' to a tenant.
    Example: 'advanced_analytics', 'bulk_export', 'sso_auth'.
    """
    feature_code = models.CharField(max_length=100)
    is_enabled = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)
    granted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('tenant', 'feature_code')

    def __str__(self):
        return f"{self.feature_code} for {self.tenant.name}"

class BillingEvent(TenantAwareModel):
    """
    Tracks external billing lifecycle events (webhooks).
    """
    provider_event_id = models.CharField(max_length=255, unique=True)
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event_type} ({self.provider_event_id})"
