from .providers.stripe import StripeProvider
from .providers.paddle import PaddleProvider
from .providers.upi import UPIProvider

class BillingFactory:
    """
    Factory to resolve billing providers based on tenant configuration.
    """
    
    @staticmethod
    def get_provider(tenant):
        """
        Returns the configured billing provider for a tenant.
        """
        provider_type = tenant.config.get('billing_provider', 'stripe')
        
        if provider_type == 'stripe':
            return StripeProvider()
        elif provider_type == 'paddle':
            return PaddleProvider()
        elif provider_type == 'upi':
            return UPIProvider()
            
        return StripeProvider() # Fallback
