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

class TenantCreditWallet(TenantAwareModel):
    """
    Chi Tier: Pre-paid Credit System.
    Tracks credits purchased and consumed by the tenant.
    """
    total_credits = models.DecimalField(max_digits=20, decimal_places=4, default=0.00)
    spent_credits = models.DecimalField(max_digits=20, decimal_places=4, default=0.00)
    last_recharge_at = models.DateTimeField(null=True, blank=True)
    
    @property
    def balance(self):
        return self.total_credits - self.spent_credits

    def __str__(self):
        return f"Wallet for {self.tenant.name} (Balance: {self.balance})"

class RevenueEntry(TenantAwareModel):
    """
    Chi Tier: Revenue Recognition (ASC 606).
    Tracks recognized revenue per month for financial compliance.
    """
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    recognized_date = models.DateField()
    description = models.CharField(max_length=255)
    source_type = models.CharField(max_length=50, default='subscription') # subscription, custom_deal
    
    class Meta:
        verbose_name_plural = "Revenue entries"

    def __str__(self):
        return f"Recognized {self.amount} on {self.recognized_date} for {self.tenant.name}"
