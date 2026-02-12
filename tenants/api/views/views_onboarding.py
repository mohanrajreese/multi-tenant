from rest_framework import viewsets, response, status, permissions
from ..serializers.serializers import OnboardingSerializer
from tenants.business.use_cases.onboarding.onboard_tenant import OnboardTenantUseCase
from tenants.business.dto import TenantOnboardingDTO

class OnboardingViewSet(viewsets.ViewSet):
    """
    Public API for tenant onboarding.
    Refactored to use Clean Architecture Use Cases (Tier 51).
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = OnboardingSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Convert serializer data to stateless DTO
        dto = TenantOnboardingDTO(**serializer.validated_data)
        
        tenant, admin_user = OnboardTenantUseCase.execute(dto)
        
        return response.Response({
            'status': 'success',
            'tenant_slug': tenant.slug,
            'admin_email': admin_user.email
        }, status=status.HTTP_201_CREATED)
