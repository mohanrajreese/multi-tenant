from .api_base import TenantAwareViewSet, DRFTenantPermission
from tenants.models import Quota, AuditLog
from ..serializers.serializers import QuotaSerializer, AuditLogSerializer

class QuotaViewSet(TenantAwareViewSet):
    queryset = Quota.objects.all()
    serializer_class = QuotaSerializer
    permission_classes = [DRFTenantPermission]

class AuditLogViewSet(TenantAwareViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [DRFTenantPermission]
    http_method_names = ['get']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        model_name = self.request.query_params.get('model_name')
        if model_name:
            queryset = queryset.filter(model_name__iexact=model_name)
            
        action_type = self.request.query_params.get('action')
        if action_type:
            queryset = queryset.filter(action__iexact=action_type)

        user_email = self.request.query_params.get('user_email')
        if user_email:
            queryset = queryset.filter(user__email__iexact=user_email)

        return queryset.order_by('-created_at')
