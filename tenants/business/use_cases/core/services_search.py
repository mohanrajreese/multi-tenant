from django.db.models import Q
from tenants.infrastructure.registry import SearchRegistry

class SearchService:
    @staticmethod
    def search(query):
        """
        Registry-based Search Engine.
        Dynamically searches across all models registered in SearchRegistry.
        """
        results = {
            'query': query
        }
        
        if not query:
            return results
        
        from tenants.infrastructure.adapters.search.factory import SearchFactory
        from tenants.infrastructure.utils.context import get_current_tenant
        
        tenant = get_current_tenant()
        if not tenant:
            return results
            
        provider = SearchFactory.get_provider(tenant)
        # Search across all registered models
        search_results = provider.search(tenant.id, query)
        
        results.update(search_results)
        return results
