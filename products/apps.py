from django.apps import AppConfig


class ProductsConfig(AppConfig):
    name = "products"

    def ready(self):
        from tenants.registry import SearchRegistry, APIRegistry
        from .models import Product
        from .api_views import ProductViewSet

        # Plug into the Multi-Tenant Search Engine
        SearchRegistry.register(
            Product,
            ['name', 'description'],
            lambda p: {'id': p.id, 'name': p.name, 'price': str(p.price)}
        )

        # Plug into the Unified API Router
        APIRegistry.register(r'products', ProductViewSet, basename='api_product')
