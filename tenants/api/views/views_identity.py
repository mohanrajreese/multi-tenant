from rest_framework import response, status, permissions, views, viewsets
from django.contrib.auth.models import Permission
from .api_base import TenantAwareViewSet, DRFTenantPermission
from tenants.domain.models import Role, Membership
from ..serializers.serializers import UserSerializer, RoleSerializer, PermissionSerializer, ChangePasswordSerializer

class MeView(views.APIView):
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
    def get_queryset(self):
        from django.conf import settings
        managed_apps = getattr(settings, 'TENANT_MANAGED_APPS', ['tenants'])
        return Permission.objects.filter(content_type__app_label__in=managed_apps)
    
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated]

class TenantSwitcherAPIView(views.APIView):
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
