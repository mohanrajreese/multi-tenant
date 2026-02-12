from rest_framework import viewsets, response, status
from rest_framework.decorators import action
from .api_base import DRFTenantPermission
from tenants.models import Tenant
from ..serializers.serializers import TenantSerializer
from tenants.business.core.services_tenant import TenantService

class TenantViewSet(viewsets.ModelViewSet):
    serializer_class = TenantSerializer
    permission_classes = [DRFTenantPermission]
    http_method_names = ['get', 'patch', 'put']

    def get_queryset(self):
        return Tenant.objects.filter(id=self.request.tenant.id)

    @action(detail=True, methods=['post'], url_path='purge-data')
    def purge(self, request, pk=None):
        tenant = self.get_object()
        if str(tenant.id) != str(request.tenant.id):
            return response.Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
            
        result = TenantService.purge_tenant_data(tenant)
        return response.Response({'status': 'purged', 'message': result})

    @action(detail=True, methods=['get'], url_path='export-data')
    def export(self, request, pk=None):
        tenant = self.get_object()
        if str(tenant.id) != str(request.tenant.id):
            return response.Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
            
        data = TenantService.export_tenant_data(tenant)
        return response.Response(data)

    @action(detail=True, methods=['post'], url_path='change-plan')
    def change_plan(self, request, pk=None):
        tenant = self.get_object()
        plan_id = request.data.get('plan_id')
        
        if not plan_id:
            return response.Response({'error': 'plan_id is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            from tenants.models import Plan
            from tenants.business.operations.services_plan import PlanService
            plan = Plan.objects.get(id=plan_id, is_active=True)
            message = PlanService.apply_plan_to_tenant(tenant, plan)
            return response.Response({'status': 'success', 'message': message})
        except Plan.DoesNotExist:
            return response.Response({'error': 'Invalid or inactive plan_id'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return response.Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
