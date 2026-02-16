
from django.db import models, transaction
from django.utils import timezone
import uuid

class LedgerAccount(models.Model):
    """
    Tier 75: Financial Ledger (Account).
    Represents a specific bucket of value for a tenant (Credits, Storage, etc.).
    """
    ACCOUNT_TYPES = [
        ('CREDIT', 'Financial Credits'),
        ('STORAGE', 'Storage Quota (MB)'),
        ('API_CALLS', 'API Request Quota'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='ledger_accounts')
    name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    balance = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('tenant', 'account_type')

    def __str__(self):
        return f"{self.tenant.slug} - {self.name} ({self.balance})"

class LedgerEntry(models.Model):
    """
    Tier 75: Financial Ledger (Entry).
    An immutable record of a value change.
    """
    ENTRY_TYPES = [
        ('CREDIT', 'Credit (Addition)'),
        ('DEBIT', 'Debit (Subtraction)'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(LedgerAccount, on_delete=models.CASCADE, related_name='entries')
    entry_type = models.CharField(max_length=10, choices=ENTRY_TYPES)
    amount = models.DecimalField(max_digits=20, decimal_places=4)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    reference_id = models.CharField(max_length=100, blank=True, help_text="ID of external transaction/event")
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.account.name}: {self.entry_type} {self.amount}"
