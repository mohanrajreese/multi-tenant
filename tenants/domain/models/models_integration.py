from django.db import models
from .base import TenantAwareModel

class Webhook(TenantAwareModel):
    target_url = models.URLField()
    secret = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    events = models.JSONField(default=list)

    def __str__(self):
        return f"Webhook for {self.tenant.name} -> {self.target_url}"

class WebhookEvent(TenantAwareModel):
    webhook = models.ForeignKey(Webhook, on_delete=models.CASCADE, related_name='deliveries')
    event_type = models.CharField(max_length=50)
    payload = models.JSONField()
    response_status = models.IntegerField(null=True, blank=True)
    response_body = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
