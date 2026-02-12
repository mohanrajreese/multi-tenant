import logging
from tenants.domain.models import Tenant
from .factory import BillingFactory

logger = logging.getLogger(__name__)

class PromotionEngine:
    """
    Sigma Tier: Enterprise Promotion & Coupon Engine.
    Orchestrates the application of discounts across providers.
    """

    @staticmethod
    def apply_coupon(tenant: Tenant, coupon_code: str) -> bool:
        """
        Validates and applies a coupon code to a tenant's subscription.
        """
        if not coupon_code:
            return False

        # In a real setup, we might have an internal 'Promotion' model
        # to track usage, expiry, and internal discount logic.
        
        provider = BillingFactory.get_provider(tenant)
        try:
            success = provider.apply_coupon(tenant, coupon_code)
            if success:
                logger.info(f"Coupon {coupon_code} applied successfully to {tenant.slug}")
                # We could store the applied coupon in tenant.config for reference
                tenant.config['applied_coupon'] = coupon_code
                tenant.save()
            return success
        except Exception as e:
            logger.error(f"Failed to apply coupon {coupon_code} for {tenant.slug}: {e}")
            return False

    @staticmethod
    def get_eligible_promotions(tenant: Tenant):
        """
        Returns a list of eligible promotions for a specific tenant.
        Enterprise logic: 'First-time customer', 'Loyalty discount', etc.
        """
        # Mock logic
        return ["WELCOME2026", "PARTNER_DISCOUNT"]
