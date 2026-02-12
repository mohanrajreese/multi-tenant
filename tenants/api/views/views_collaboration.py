from rest_framework import response, status, permissions, views, serializers, viewsets
from rest_framework.decorators import action
from .api_base import TenantAwareViewSet, DRFTenantPermission
from tenants.domain.models import TenantInvitation, Membership
from ..serializers.serializers import TenantInvitationSerializer, MembershipSerializer
from tenants.business.use_cases.operations.services_invitation import InvitationService

class TenantInvitationViewSet(TenantAwareViewSet):
    queryset = TenantInvitation.objects.all()
    serializer_class = TenantInvitationSerializer
    permission_classes = [DRFTenantPermission]

    def perform_create(self, serializer):
        try:
            InvitationService.create_invitation(
                tenant=self.request.tenant,
                invited_by=self.request.user,
                email=serializer.validated_data['email'],
                role_name=serializer.validated_data['role'].name
            )
        except Exception as e:
            raise serializers.ValidationError(str(e))

    @action(detail=True, methods=['post'])
    def resend(self, request, pk=None):
        invitation = self.get_object()
        try:
            InvitationService.resend_invitation(invitation.id, request.tenant)
            return response.Response({'status': 'invitation resent'})
        except Exception as e:
            return response.Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        invitation = self.get_object()
        try:
            InvitationService.revoke_invitation(invitation.id, request.tenant)
            return response.Response({'status': 'invitation revoked'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return response.Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class MembershipViewSet(TenantAwareViewSet):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer
    permission_classes = [DRFTenantPermission]
    http_method_names = ['get', 'patch', 'put', 'delete']

class AcceptInvitationAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, token):
        try:
            invitation = TenantInvitation.objects.get(token=token, is_accepted=False)
            if invitation.is_expired():
                 return response.Response({'error': 'Invitation expired'}, status=status.HTTP_400_BAD_REQUEST)
            
            Membership.objects.create(
                user=request.user,
                tenant=invitation.tenant,
                role=invitation.role
            )
            invitation.is_accepted = True
            invitation.save()
            return response.Response({'status': 'success', 'tenant': invitation.tenant.name})
        except TenantInvitation.DoesNotExist:
            return response.Response({'error': 'Invalid or already accepted token'}, status=status.HTTP_404_NOT_FOUND)
