from django.db import models
from django.conf import settings
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
    expires_at = models.DateTimeField(null=True, blank=True)
    granted_at = models.DateTimeField(auto_now_add=True)
    
    # Sigma Tier: Inheritance
    plan = models.ForeignKey('tenants.Plan', on_delete=models.CASCADE, null=True, blank=True, related_name='entitlements')

    class Meta:
        unique_together = ('tenant', 'feature_code')

    def is_valid(self):
        from django.utils import timezone
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return self.is_enabled

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

class GovernanceRequest(TenantAwareModel):
    """
    Tier 46: Trust & Scaling Sovereignty - Dual Control.
    Implements 'Four-Eyes' principle for destructive actions.
    """
    ACTION_CHOICES = (
        ('PURGE', 'Permanent Organization Purge'),
        ('EXPORT', 'Sensitive Data Export'),
    )
    STATUS_CHOICES = (
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('EXECUTED', 'Executed'),
    )

    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES)
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='governance_requests')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='governance_approvals')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    executed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def can_execute(self) -> bool:
        return self.status == 'APPROVED' and self.approved_by is not None and self.approved_by != self.requested_by
