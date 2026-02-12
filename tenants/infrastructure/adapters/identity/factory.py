from .providers.google import GoogleSSOAdapter
from .providers.okta import OktaSSOAdapter
from .providers.azure import AzureSSOAdapter

class IdentityFactory:
    """
    Sovereign Identity Resolver.
    """
    
    @staticmethod
    def get_provider(tenant):
        config = tenant.sso_config
        provider_type = config.get('provider', 'google')
        
        if provider_type == 'google':
            return GoogleSSOAdapter(config)
        elif provider_type == 'okta':
            return OktaSSOAdapter(config)
        elif provider_type == 'azure':
            return AzureSSOAdapter(config)
        
        return GoogleSSOAdapter(config)
