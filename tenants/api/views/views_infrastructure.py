from rest_framework import response, status, views
from rest_framework.decorators import action
from .api_base import TenantAwareViewSet, DRFTenantPermission
from tenants.domain.models import Domain, Quota
from ..serializers.serializers import DomainSerializer
from tenants.business.use_cases.core.services_domain import DomainService
from tenants.business.use_cases.core.services_search import SearchService

class DomainViewSet(TenantAwareViewSet):
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer
    permission_classes = [DRFTenantPermission]

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        domain = self.get_object()
        if DomainService.verify_dns(domain):
            domain.status = 'ACTIVE'
            domain.save()
            return response.Response({'status': 'verified', 'domain_status': domain.status})
        return response.Response({'status': 'verification_failed', 'domain_status': domain.status}, status=status.HTTP_400_BAD_REQUEST)

class GlobalSearchAPIView(views.APIView):
    permission_classes = [DRFTenantPermission]

    def get(self, request):
        query = request.GET.get('q', '')
        results = SearchService.search(query)
        return response.Response(results)

class HealthCheckAPIView(views.APIView):
    permission_classes = [DRFTenantPermission]

    def get(self, request):
        tenant = request.tenant
        quotas = Quota.objects.filter(tenant=tenant)
        quota_data = {q.resource_name: {'limit': q.limit_value, 'usage': q.current_usage} for q in quotas}
        
        return response.Response({
            'status': 'healthy',
            'tenant': tenant.name,
            'maintenance_mode': tenant.is_maintenance,
            'storage_prefix': f"tenants/{tenant.id}/",
            'quotas': quota_data
        })
