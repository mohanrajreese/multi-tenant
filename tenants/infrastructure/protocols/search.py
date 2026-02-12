from typing import Protocol, runtime_checkable, Any, List, Dict

@runtime_checkable
class ISearchProvider(Protocol):
    """
    Tier 61: Search Sovereignty Protocol.
    Abstracts full-text search engines (Postgres, Elasticsearch).
    """
    def index_document(self, tenant_id: str, model_name: str, object_id: str, content: Dict[str, Any], **kwargs: Any) -> bool:
        """Index a document for searching."""
        ...

    def search(self, tenant_id: str, query: str, models: List[str] = None, **kwargs: Any) -> Dict[str, List[Any]]:
        """Search across indexed documents."""
        ...
