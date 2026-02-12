from tenants.infrastructure.protocols.search import ISearchProvider
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models import F
import logging

logger = logging.getLogger(__name__)

class PostgresFullTextProvider(ISearchProvider):
    """
    Tier 61: Native PostgreSQL Full-Text Search.
    Uses 'django.contrib.postgres' for lexeme-based search independently per tenant.
    """
    def index_document(self, tenant_id, model_name, object_id, content, **kwargs):
        # Postgres FTS is real-time; no separate indexing step needed usually 
        # unless using a dedicated SearchVectorField.
        # For this implementation, we assume dynamic runtime search or 
        # a dedicated SearchIndex model could be updated here.
        return True

    def search(self, tenant_id, query, models=None, **kwargs):
        from tenants.infrastructure.registry import SearchRegistry
        
        results = {}
        # We iterate over registered models and perform FTS
        for entry in SearchRegistry.get_entries():
            model = entry['model']
            fields = entry['fields']
            serializer = entry['serializer']
            
            # Skip if model filtering is active
            if models and model._meta.model_name not in models:
                continue

            # Build SearchVector dynamically
            vector = SearchVector(*fields)
            search_query = SearchQuery(query)
            
            queryset = model.objects.annotate(
                rank=SearchRank(vector, search_query)
            ).filter(rank__gte=0.1).order_by('-rank')[:5]
            
            results[model._meta.model_name] = [serializer(obj) for obj in queryset]
            
        return results

class ElasticsearchProvider(ISearchProvider):
    """
    Tier 61: Enterprise Search (Elasticsearch/OpenSearch).
    """
    def __init__(self, config=None):
        self.config = config or {}
        self.host = self.config.get('host', 'http://localhost:9200')
        self.index_prefix = self.config.get('index_prefix', 'tenant')

    def index_document(self, tenant_id, model_name, object_id, content, **kwargs):
        # Mocking the HTTP call to ES
        index = f"{self.index_prefix}_{tenant_id}_{model_name.lower()}"
        logger.info(f"[Elasticsearch] Indexing {object_id} into {index}")
        return True

    def search(self, tenant_id, query, models=None, **kwargs):
        # Mocking the Search result
        logger.info(f"[Elasticsearch] Searching for '{query}' in tenant {tenant_id}")
        return {
            "summary": "Results from Elasticsearch", 
            "hits": []
        }
