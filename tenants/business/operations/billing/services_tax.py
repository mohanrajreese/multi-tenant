import logging
from tenants.models import Tenant
from .factory import BillingFactory

logger = logging.getLogger(__name__)

class TaxService:
    """
    Sigma Tier: Advanced Tax Sovereignty Service.
    Agnostic interface for tax calculation and compliance (VAT/GST).
    """

    @staticmethod
    def calculate_taxes(tenant: Tenant, amount: float) -> float:
        """
        Calculates the tax amount for a given transaction.
        Delegates to the active billing provider's tax engine.
        """
        if not tenant.country_code or not tenant.billing_address:
            logger.warning(f"Tenant {tenant.slug} missing tax data. Returning zero tax.")
            return 0.0

        provider = BillingFactory.get_provider(tenant)
        try:
            tax_amount = provider.calculate_taxes(tenant, amount)
            logger.info(f"Tax calculated for {tenant.slug}: {tax_amount} (on {amount})")
            return tax_amount
        except Exception as e:
            logger.error(f"Tax calculation failed for {tenant.slug}: {e}")
            return 0.0

    @staticmethod
    def validate_tax_id(tax_id: str, country_code: str) -> bool:
        """
        Validates a tax identifier (e.g., VAT number) for a specific country.
        In production, this would call a validation API (e.g., Stripe Tax, VIES).
        """
        # LIVE API HOOK: In production, call TaxJar/Avalara/VIES here.
        # response = requests.get(f"https://api.vies.eu/validate/{tax_id}")
        if not tax_id:
            return False
        return len(tax_id) > 5 # Basic check
