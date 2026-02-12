import logging
from tenants.models import Tenant
from tenants.models.models_billing import Entitlement
from .factory import BillingFactory

logger = logging.getLogger(__name__)

class EntitlementReconciler:
    """
    Tier 45: Managed Revenue Leakage Protection.
    Reconciles local feature-gates with external billing provider status.
    """

    @staticmethod
    def reconcile_tenant(tenant: Tenant):
        """
        Synchronizes the tenant's local state with the source-of-truth 
        from the billing provider (Stripe/Paddle).
        """
        if not tenant.subscription_id:
            logger.warning(f"Tenant {tenant.slug} has no subscription ID. Skipping reconciliation.")
            return

        try:
            provider = BillingFactory.get_provider(tenant)
            # In production, this would call provider.get_subscription_status(tenant.subscription_id)
            # mock status for now
            remote_status = 'active' # Mocked from provider
            
            logger.info(f"Reconciling {tenant.slug}. Local: {tenant.subscription_status}, Remote: {remote_status}")
            
            if remote_status != tenant.subscription_status:
                logger.warning(f"Status mismatch detected for {tenant.slug}. Syncing to {remote_status}")
                tenant.subscription_status = remote_status
                if remote_status in ['canceled', 'past_due']:
                    tenant.is_active = False
                    # Disable all custom entitlements
                    Entitlement.objects.filter(tenant=tenant).update(is_enabled=False)
                elif remote_status == 'active':
                    tenant.is_active = True
                    Entitlement.objects.filter(tenant=tenant).update(is_enabled=True)
                
                tenant.save()
                
        except Exception as e:
            logger.error(f"Failed to reconcile entitlement for {tenant.slug}: {str(e)}")

    @staticmethod
    def run_global_reconciliation():
        """
        Periodic task to scan all active tenants and ensure no revenue leakage.
        """
        for tenant in Tenant.objects.all():
            EntitlementReconciler.reconcile_tenant(tenant)
