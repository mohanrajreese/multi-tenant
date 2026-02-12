from .providers.stripe import StripeProvider
from tenants.infrastructure.utils import get_current_tenant

class BillingFactory:
    """
    Omega Tier: Dynamic Billing Provider Resolver.
    """
    
    @staticmethod
    def get_provider(tenant=None):
        """
        Returns the appropriate billing provider for the tenant.
        By default, we use our StripeProvider.
        """
        # In a multi-provider setup, we would read tenant.config['billing_provider']
        return StripeProvider()
