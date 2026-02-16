from uuid import uuid4
from django.db import models
from tenants.infrastructure.storage.utils import tenant_storage_path
from tenants.infrastructure.storage.factory import get_tenant_storage

class Plan(models.Model):
    """
    Subscription tiers for the platform.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    default_quotas = models.JSONField(default=dict)
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    yearly_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class Tenant(models.Model):
    """
    The Organization/Client that owns data.
    """
    ISOLATION_CHOICES = (
        ('LOGICAL', 'Logical Isolation (Shared Table)'),
        ('PHYSICAL', 'Physical Isolation (PostgreSQL Schema)'),
    )

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, help_text="Unique name for the tenant (e.g., acme-corp)")
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True, related_name='tenants')
    isolation_mode = models.CharField(max_length=20, choices=ISOLATION_CHOICES, default='LOGICAL')
    
    logo = models.ImageField(
        upload_to=tenant_storage_path, 
        storage=get_tenant_storage, 
        null=True, 
        blank=True
    )
    primary_color = models.CharField(max_length=7, default="#000000", help_text="Hex color code")
    secondary_color = models.CharField(max_length=7, default="#ffffff", help_text="Hex color code")
    support_email = models.EmailField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    is_maintenance = models.BooleanField(default=False)
    config = models.JSONField(default=dict, blank=True)
    ip_whitelist = models.JSONField(default=list, blank=True)
    security_config = models.JSONField(default=dict, blank=True)
    smtp_config = models.JSONField(default=dict, blank=True)
    sso_config = models.JSONField(default=dict, blank=True)
    storage_config = models.JSONField(default=dict, blank=True)
    
    # Omega Tier: Monetization
    billing_customer_id = models.CharField(max_length=255, null=True, blank=True)
    subscription_id = models.CharField(max_length=255, null=True, blank=True)
    subscription_status = models.CharField(
        max_length=50, 
        default='active',
        help_text="active, past_due, trialing, canceled"
    )

    # Sigma Tier: Tax & Billing Sovereignty
    tax_id = models.CharField(max_length=100, null=True, blank=True, help_text="VAT/GST/EIN")
    billing_address = models.TextField(null=True, blank=True)
    country_code = models.CharField(max_length=2, default="US", help_text="ISO 2-letter country code")
    preferred_currency = models.CharField(max_length=3, default="USD", help_text="ISO 3-letter currency code (e.g., USD, EUR, GBP)")
    timezone = models.CharField(max_length=100, default="UTC", help_text="Olson timezone name")
    locale = models.CharField(max_length=10, default="en-US", help_text="BCP 47 language tag")

    # Tier 98: Organizational Hierarchy
    parent = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='children',
        help_text="Parent organization for hierarchical multi-tenancy"
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_ancestors(self, include_self=True):
        """
        Tier 98: Hierarchy Traversal.
        Returns a list of all parent organizations in ascending order.
        """
        ancestors = [self] if include_self else []
        curr = self.parent
        while curr:
            ancestors.append(curr)
            curr = curr.parent
        return ancestors

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
