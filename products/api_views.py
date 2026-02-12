from rest_framework.decorators import action
from rest_framework import status, response
from tenants.api_base import TenantAwareViewSet, DRFTenantPermission
from tenants.services_bulk import BulkImportService
from .models import Product
from .serializers import ProductSerializer

class ProductViewSet(TenantAwareViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [DRFTenantPermission]

    @action(detail=False, methods=['post'], url_path='bulk-import')
    def bulk_import(self, request):
        """
        Mythical Tier: Bulk import products in a single transaction.
        """
        data_list = request.data.get('items', [])
        if not isinstance(data_list, list) or not data_list:
            return response.Response(
                {'error': 'A non-empty list of "items" is required.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            results = BulkImportService.bulk_import(
                tenant=request.tenant,
                model_class=Product,
                data_list=data_list,
                serializer_class=ProductSerializer
            )
            return response.Response({
                'status': 'success',
                'created_count': results['created']
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return response.Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
