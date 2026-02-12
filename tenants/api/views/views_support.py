from rest_framework import viewsets, response, status, permissions
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from ..serializers.serializers import ImpersonationSerializer

User = get_user_model()

class ImpersonationViewSet(viewsets.ViewSet):
    """
    Omega Tier: Secure Support Impersonation API.
    Only accessible by staff members.
    """
    permission_classes = [permissions.IsAdminUser]
    serializer_class = ImpersonationSerializer

    @action(detail=False, methods=['post'])
    def start(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_id = serializer.validated_data['user_id']
        reason = serializer.validated_data['reason']
        
        try:
            target_user = User.objects.get(id=user_id)
            
            # Store the real admin's ID in the session
            request.session['impersonator_id'] = str(request.user.id)
            
            # Log the start of impersonation
            from tenants.business.use_cases.security.services_audit import AuditService
            from tenants.domain.models import AuditLog
            # Note: We don't use the standard signal here because it's a session change, not a model change
            
            print(f"[SECURITY] Staff {request.user.email} started impersonating {target_user.email}. Reason: {reason}")
            
            return response.Response({
                'status': 'success',
                'message': f"Now impersonating {target_user.email}",
                'target_user': str(target_user.id)
            })
            
        except User.DoesNotExist:
            return response.Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def stop(self, request):
        if 'impersonator_id' in request.session:
            del request.session['impersonator_id']
            return response.Response({'status': 'success', 'message': 'Impersonation ended'})
        return response.Response({'error': 'No active impersonation session'}, status=status.HTTP_400_BAD_REQUEST)
