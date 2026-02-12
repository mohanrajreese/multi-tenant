from .api_base import TenantAwareViewSet, DRFTenantPermission
from .models import AuditLog, Membership, TenantInvitation, Role, Domain, Tenant, Quota
from .serializers import (
    AuditLogSerializer, OnboardingSerializer, TenantInvitationSerializer,
    UserSerializer, RoleSerializer, DomainSerializer, TenantSerializer,
    MembershipSerializer, ChangePasswordSerializer, PermissionSerializer,
    QuotaSerializer
)
from .services import TenantService
from .services_search import SearchService
from .services_invitation import InvitationService
from .services_domain import DomainService
from rest_framework import viewsets, permissions, response, status, views, serializers
from rest_framework.decorators import action

class OnboardingViewSet(viewsets.ViewSet):
    """
    Public API for tenant onboarding.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = OnboardingSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                tenant, admin_user = TenantService.onboard_tenant(**serializer.validated_data)
                return response.Response({
                    'status': 'success',
                    'tenant_slug': tenant.slug,
                    'admin_email': admin_user.email
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return response.Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TenantInvitationViewSet(TenantAwareViewSet):
    queryset = TenantInvitation.objects.all()
    serializer_class = TenantInvitationSerializer
    permission_classes = [DRFTenantPermission]

    def perform_create(self, serializer):
        from .services_invitation import InvitationService
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

class GlobalSearchAPIView(views.APIView):
    """
    Headless JSON Search API.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        query = request.GET.get('q', '')
        results = SearchService.search(query)
        # SearchService now returns a dictionary of already-serialized results
        return response.Response(results)

class MeView(views.APIView):
    """
    Identity API: Returns the current user's profile and their role in the current tenant.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        tenant = getattr(request, 'tenant', None)
        membership = None
        if tenant:
            membership = Membership.objects.filter(user=request.user, tenant=tenant).first()
        
        data = UserSerializer(request.user).data
        data['tenant'] = tenant.name if tenant else None
        data['role'] = membership.role.name if membership and membership.role else None
        return response.Response(data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(views.APIView):
    """
    Headless password update API.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            return response.Response({'status': 'password updated'})
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RoleViewSet(TenantAwareViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [DRFTenantPermission]

class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Discovery API for available permissions.
    """
    def get_queryset(self):
        from django.conf import settings
        managed_apps = getattr(settings, 'TENANT_MANAGED_APPS', ['tenants'])
        return Permission.objects.filter(content_type__app_label__in=managed_apps)
    
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated]

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

class TenantViewSet(viewsets.ModelViewSet):
    """
    Manage the current tenant's global settings.
    """
    serializer_class = TenantSerializer
    permission_classes = [DRFTenantPermission]
    http_method_names = ['get', 'patch', 'put']

    def get_queryset(self):
        return Tenant.objects.filter(id=self.request.tenant.id)

    @action(detail=True, methods=['post'], url_path='purge-data')
    def purge(self, request, pk=None):
        """
        Compliance: Hard delete all tenant data.
        """
        tenant = self.get_object()
        # Security: Double check it's the current tenant
        if str(tenant.id) != str(request.tenant.id):
            return response.Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
            
        result = TenantService.purge_tenant_data(tenant)
        return response.Response({'status': 'purged', 'message': result})

    @action(detail=True, methods=['get'], url_path='export-data')
    def export(self, request, pk=None):
        """
        GDPR Portability: Download all tenant data.
        """
        tenant = self.get_object()
        # Security: Double check it's the current tenant
        if str(tenant.id) != str(request.tenant.id):
            return response.Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
            
        data = TenantService.export_tenant_data(tenant)
        return response.Response(data)

    @action(detail=True, methods=['post'], url_path='change-plan')
    def change_plan(self, request, pk=None):
        """
        Billing: Headlessly change the tenant's subscription plan.
        """
        tenant = self.get_object()
        plan_id = request.data.get('plan_id')
        
        if not plan_id:
            return response.Response({'error': 'plan_id is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            from .models import Plan
            from .services_plan import PlanService
            plan = Plan.objects.get(id=plan_id, is_active=True)
            message = PlanService.apply_plan_to_tenant(tenant, plan)
            return response.Response({'status': 'success', 'message': message})
        except Plan.DoesNotExist:
            return response.Response({'error': 'Invalid or inactive plan_id'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return response.Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class QuotaViewSet(TenantAwareViewSet):
    """
    Manage resource limits headlessly.
    """
    queryset = Quota.objects.all()
    serializer_class = QuotaSerializer
    permission_classes = [DRFTenantPermission]

class AcceptInvitationAPIView(views.APIView):
    """
    Headless path for accepting a team invitation.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, token):
        try:
            invitation = TenantInvitation.objects.get(token=token, is_accepted=False)
            # Use the existing service logic
            from .views import AcceptInvitationView
            # In a headless API, we might want a dedicated service method
            # For now, we'll implement the core logic:
            if invitation.expires_at < invitation.created_at.now():
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

class MembershipViewSet(TenantAwareViewSet):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer
    permission_classes = [DRFTenantPermission]
    # Enabled full CRUD for team management via API
    http_method_names = ['get', 'patch', 'put', 'delete']

class AuditLogViewSet(TenantAwareViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [DRFTenantPermission]
    http_method_names = ['get'] # Audit logs are read-only via API

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Advanced Filtering
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

class HealthCheckAPIView(views.APIView):
    """
    Tenant-scoped health and observability API.
    """
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

class TenantSwitcherAPIView(views.APIView):
    """
    Zenith Tier: User Discovery API.
    Returns all tenants the user is a member of.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        memberships = Membership.objects.filter(user=request.user, is_active=True)
        results = []
        for m in memberships:
            t = m.tenant
            primary_domain = t.domains.filter(is_primary=True, status='ACTIVE').first()
            results.append({
                'id': str(t.id),
                'name': t.name,
                'slug': t.slug,
                'role': m.role.name if m.role else None,
                'primary_domain': primary_domain.domain if primary_domain else None,
                'logo': request.build_absolute_uri(t.logo.url) if t.logo else None
            })
        return response.Response(results)
