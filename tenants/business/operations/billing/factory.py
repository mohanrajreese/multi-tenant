from .providers.stripe import StripeProvider
from .providers.paddle import PaddleProvider
from tenants.infrastructure.utils import get_current_tenant

class BillingFactory:
    """
    Omega Tier: Dynamic Billing Provider Resolver.
    Supports multi-provider orchestration (Stripe, Paddle, etc.).
    """
    
    @staticmethod
    def get_provider(tenant=None):
        """
        Returns the appropriate billing provider for the tenant.
        Defaults to Stripe unless explicitly configured otherwise.
        """
        if tenant is None:
            tenant = get_current_tenant()
            
        if not tenant:
            return StripeProvider() # Fallback

        provider_type = tenant.config.get('billing_provider', 'stripe').lower()
        
        if provider_type == 'paddle':
            return PaddleProvider()
        return StripeProvider()
