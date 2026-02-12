import logging
from ..base import BillingProvider

logger = logging.getLogger(__name__)

class OfflinePaymentProvider(BillingProvider):
    """
    Tier 45: Enterprise Sovereignty.
    Handles 'Custom Contracts' (Bank Transfer/Net-30) for Fortune 500 clients.
    """

    def create_customer(self, tenant):
        logger.info(f"Creating offline customer record for {tenant.slug}")
        return f"OFFLINE_{tenant.id}"

    def create_subscription(self, tenant, plan_id):
        logger.info(f"Establishing custom contract subscription for {tenant.slug}")
        return f"CONTRACT_{tenant.id}"

    def cancel_subscription(self, subscription_id):
        logger.warning(f"Terminating custom contract {subscription_id}")
        return True

    def get_portal_url(self, tenant):
        # Enterprise clients usually have a dedicated account manager / PDF invoice pool
        return "mailto:billing-support@sovereign.engine"

    def update_quantity(self, subscription_id, quantity):
        logger.info(f"Updating contract seat count for {subscription_id} to {quantity}")
        return True

    def verify_webhook(self, payload, signature):
        # Offline payments don't use standard webhooks; they are processed via reconciliation tasks
        return True
