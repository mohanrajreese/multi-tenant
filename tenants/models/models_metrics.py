from django.db import models
from .base import TenantAwareModel

class TenantMetric(TenantAwareModel):
    metric_name = models.CharField(max_length=100)
    value = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    unit = models.CharField(max_length=20, default='count')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.metric_name}: {self.value} {self.unit}"
