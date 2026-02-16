
from django.db import models
from tenants.domain.models import TenantAwareModel

class TelemetryEntry(TenantAwareModel):
    """
    Tier 94: Observability Sovereignty.
    Persists infrastructure outcomes (success/failure/latency) 
    for tenant-level visibility.
    """
    PROVIDER_CHOICES = [
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
        ('WHATSAPP', 'WhatsApp'),
        ('SEARCH', 'Search'),
        ('CACHE', 'Cache'),
        ('IDENTITY', 'Identity'),
    ]

    STATUS_CHOICES = [
        ('SUCCESS', 'Success'),
        ('FAILURE', 'Failure'),
        ('DEGRADED', 'Degraded (Fallback Used)'),
        ('CIRCUIT_OPEN', 'Circuit Breaker Open'),
    ]

    provider = models.CharField(max_length=50, choices=PROVIDER_CHOICES)
    action = models.CharField(max_length=100) # e.g. "send_email", "index_doc"
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    latency_ms = models.IntegerField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    metadata = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Telemetry Entries"
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.status}] {self.provider} - {self.action} ({self.tenant.slug})"
