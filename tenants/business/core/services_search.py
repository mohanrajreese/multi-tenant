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
            
        for entry in SearchRegistry.get_entries():
            model = entry['model']
            fields = entry['fields']
            serializer = entry['serializer']
            
            # Build dynamic search filter
            search_query = Q()
            for field in fields:
                search_query |= Q(**{f"{field}__icontains": query})
            
            # Execute search (TenantManager handles isolation automatically)
            queryset = model.objects.filter(search_query)[:5]
            
            # Store results by model name
            results[model._meta.model_name] = [serializer(obj) for obj in queryset]
            
        return results
