from .providers import DatabaseAuditProvider, SplunkProvider, DatadogProvider

class AuditFactory:
    """
    Tier 59: Compliance Resolution Factory.
    """
    @staticmethod
    def get_provider(tenant):
        config = tenant.config.get('audit', {})
        provider_type = config.get('provider', 'database')
        
        if provider_type == 'splunk':
            return SplunkProvider(config)
        elif provider_type == 'datadog':
            return DatadogProvider(config)
            
        return DatabaseAuditProvider()
