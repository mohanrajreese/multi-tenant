from tenants.api_base import TenantAwareViewSet, DRFTenantPermission
from .models import Product
from .serializers import ProductSerializer

class ProductViewSet(TenantAwareViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [DRFTenantPermission]
