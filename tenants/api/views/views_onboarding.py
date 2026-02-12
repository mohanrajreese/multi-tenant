from rest_framework import viewsets, response, status, permissions
from ..serializers.serializers import OnboardingSerializer
from tenants.business.core.services_onboarding import OnboardingService

class OnboardingViewSet(viewsets.ViewSet):
    """
    Public API for tenant onboarding.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = OnboardingSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        tenant, admin_user = OnboardingService.onboard_tenant(**serializer.validated_data)
        return response.Response({
            'status': 'success',
            'tenant_slug': tenant.slug,
            'admin_email': admin_user.email
        }, status=status.HTTP_201_CREATED)
