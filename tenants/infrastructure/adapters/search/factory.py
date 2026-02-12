from .providers import PostgresFullTextProvider, ElasticsearchProvider

class SearchFactory:
    """
    Tier 61: Search Resolution Factory.
    """
    @staticmethod
    def get_provider(tenant):
        config = tenant.config.get('search', {})
        provider_type = config.get('provider', 'postgres')
        
        if provider_type == 'elasticsearch':
            return ElasticsearchProvider(config)
            
        return PostgresFullTextProvider()
