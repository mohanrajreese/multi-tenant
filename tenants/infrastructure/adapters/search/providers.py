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
    Provides physical isolation via tenant-prefixed indices.
    """
    def __init__(self, config=None):
        self.config = config or {}
        self.host = self.config.get('host', 'http://localhost:9200')
        self.index_prefix = self.config.get('index_prefix', 'tenant')

    def _get_client(self):
        try:
            from elasticsearch import Elasticsearch
            return Elasticsearch([self.host])
        except ImportError:
            logger.error("[Elasticsearch] Library not installed. Using Log Mock.")
            return None

    def index_document(self, tenant_id, model_name, object_id, content, **kwargs):
        index = f"{self.index_prefix}_{tenant_id}_{model_name.lower()}"
        client = self._get_client()
        
        if not client:
            logger.info(f"[Elasticsearch MOCK] Indexing {object_id} into {index}")
            return True

        try:
            client.index(index=index, id=object_id, document=content)
            logger.info(f"[Elasticsearch] Indexed {object_id} into {index}")
            return True
        except Exception as e:
            logger.error(f"[Elasticsearch] Index Error: {e}")
            return False

    def search(self, tenant_id, query, models=None, **kwargs):
        client = self._get_client()
        index = f"{self.index_prefix}_{tenant_id}_*" # Search across tenant indices
        
        if not client:
            logger.info(f"[Elasticsearch MOCK] Searching for '{query}' in {index}")
            return {"hits": [], "total": 0}

        try:
            body = {
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["*"]
                    }
                }
            }
            res = client.search(index=index, body=body)
            return {
                "hits": [hit['_source'] for hit in res['hits']['hits']],
                "total": res['hits']['total']['value']
            }
        except Exception as e:
            logger.error(f"[Elasticsearch] Search Error: {e}")
            return {"hits": [], "total": 0}
