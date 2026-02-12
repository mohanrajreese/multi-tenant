from tenants.domain.models import TenantMetric
from django.db.models import Sum
from django.utils import timezone

class MetricsService:
    """
    Apex Tier: Usage-based consumption tracking.
    """

    @staticmethod
    def record_usage(tenant, metric_name, value=1.0, unit='count'):
        """
        Logs a single usage event and pushes to the billing provider.
        """
        metric = TenantMetric.objects.create(
            tenant=tenant,
            metric_name=metric_name,
            value=value,
            unit=unit
        )
        
        # Omega Tier: Metered Billing push
        from tenants.business.use_cases.billing.factory import BillingFactory
        # Omega Tier: Metered Billing Sync
        provider = BillingFactory.get_provider(tenant)
        try:
            # Assuming quantity should be an integer for update_usage, similar to original implementation
            provider.update_usage(tenant, metric_name, int(value))
        except Exception as e:
            logger.error(f"Failed to sync metered usage for {tenant.slug}: {e}")

        # Chi Tier: Credit Drawdown Logic
        if tenant.config.get('billing', {}).get('use_credits', False):
            from tenants.business.use_cases.billing.services_wallet import CreditWalletService
            # Assume 1 credit per unit of usage for demo
            CreditWalletService.drawdown(tenant, float(value))
        
        return metric

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
