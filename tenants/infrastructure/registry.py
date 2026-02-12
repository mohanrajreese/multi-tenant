class SearchRegistry:
    """
    Registry for models to participate in the Global Search Engine.
    This allows the 'tenants' app to be project-agnostic.
    """
    _models = {}

    @classmethod
    def register(cls, model_class, search_fields, serializer_func=None):
        """
        Registers a model for the global search algorithm.
        
        Args:
            model_class: The Django Model class.
            search_fields: List of field names (strings) to search against.
            serializer_func: Lambda or function (obj) -> dict for result formatting.
        """
        cls._models[model_class._meta.label] = {
            'model': model_class,
            'fields': search_fields,
            'serializer': serializer_func or (lambda obj: {'id': obj.id, 'label': str(obj)})
        }

    @classmethod
    def get_entries(cls):
        return cls._models.values()

class APIRegistry:
    """
    Registry for external ViewSets to be automatically 
    included in the main 'tenants' API router.
    """
    _viewsets = []

    @classmethod
    def register(cls, prefix, viewset, basename=None):
        """
        Registers a ViewSet for auto-routing.
        """
        cls._viewsets.append((prefix, viewset, basename))

    @classmethod
    def get_viewsets(cls):
        return cls._viewsets
