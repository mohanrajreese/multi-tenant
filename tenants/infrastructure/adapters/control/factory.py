from .providers import DatabaseFlagProvider, LaunchDarklyProvider

class ControlFactory:
    """
    Tier 66: Control Resolution Factory.
    """
    @staticmethod
    def get_provider(tenant):
        config = tenant.config.get('control', {})
        provider_type = config.get('provider', 'database')
        
        if provider_type == 'launchdarkly':
            return LaunchDarklyProvider(config)
            
        return DatabaseFlagProvider()
