from tenants.models import TenantMetric
from django.db.models import Sum
from django.utils import timezone

class MetricsService:
    """
    Apex Tier: Usage-based consumption tracking.
    """

    @staticmethod
    def record_usage(tenant, metric_name, value=1.0, unit='count'):
        """
        Logs a single usage event.
        """
        return TenantMetric.objects.create(
            tenant=tenant,
            metric_name=metric_name,
            value=value,
            unit=unit
        )

    @staticmethod
    def get_aggregate_usage(tenant, metric_name, start_date=None):
        """
        Returns total usage for a given metric since start_date.
        """
        queryset = TenantMetric.objects.filter(tenant=tenant, metric_name=metric_name)
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
            
        return queryset.aggregate(total=Sum('value'))['total'] or 0.0

    @staticmethod
    def get_monthly_usage(tenant, metric_name):
        """
        Helper for standard billing cycles.
        """
        first_day = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return MetricsService.get_aggregate_usage(tenant, metric_name, start_date=first_day)
