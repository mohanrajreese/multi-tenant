import logging
from tenants.models import Tenant, Membership
from .factory import BillingFactory

logger = logging.getLogger(__name__)

class SeatService:
    """
    Sigma Tier: B2B Seat-Based Billing Service.
    Orchestrates the synchronization of billable user counts with providers.
    """

    @staticmethod
    def get_billable_count(tenant: Tenant) -> int:
        """
        Returns the current number of active memberships for a tenant.
        Enterprise logic could exclude certain roles (e.g., 'Internal Support').
        """
        return Membership.objects.filter(tenant=tenant, is_active=True).count()

    @staticmethod
    def sync_seats(tenant: Tenant):
        """
        Synchronizes the current seat count with the active billing provider.
        """
        if not tenant.subscription_id and tenant.config.get('billing_provider') != 'paddle':
            # Skip if no active subscription (Paddle might not need a sub_id upfront)
            return

        count = SeatService.get_billable_count(tenant)
        provider = BillingFactory.get_provider(tenant)
        
        try:
            provider.update_quantity(tenant, count)
            logger.info(f"Successfully synced {count} seats for tenant {tenant.slug}")
        except Exception as e:
            logger.error(f"Failed to sync seats for {tenant.slug}: {e}")

    @staticmethod
    def handle_membership_change(tenant: Tenant):
        """
        Triggered by signals when members are added or removed.
        In production, this should be offloaded to a background task.
        """
        # We perform a sync. In a billion-user system, we might debounce this.
        SeatService.sync_seats(tenant)
