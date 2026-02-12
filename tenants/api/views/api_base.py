from rest_framework import viewsets, permissions, exceptions
from tenants.domain.models import Membership

class TenantAwareViewSet(viewsets.ModelViewSet):
    """
    Base ViewSet that automatically filters the queryset by the current tenant.
    """
    def get_queryset(self):
        # Our TenantManager ALREADY filters by request.tenant if it's set in context.
        # However, to be extra safe and explicit for APIs, we can re-filter.
        tenant = getattr(self.request, 'tenant', None)
        if not tenant:
            return self.queryset.none()
        return self.queryset.filter(tenant=tenant)

class DRFTenantPermission(permissions.BasePermission):
    """
    Maps DRF actions to our custom tenant permissions.
    """
    def has_permission(self, request, view):
        tenant = getattr(request, 'tenant', None)
        if not tenant or not request.user.is_authenticated:
            return False

        # Look up the user's role for this specific tenant
        try:
            membership = Membership.objects.get(user=request.user, tenant=tenant)
            user_role = membership.role
        except Membership.DoesNotExist:
            return False

        # Map DRF actions to codenames
        # Note: You can expand this mapping as needed
        action_map = {
            'list': 'view',
            'retrieve': 'view',
            'create': 'add',
            'update': 'change',
            'partial_update': 'change',
            'destroy': 'delete',
        }
        
        # Get the required base permission (e.g., 'add', 'view')
        required_base = action_map.get(view.action, 'view')
        
        # Determine the model name (e.g., 'product')
        model_name = view.queryset.model._meta.model_name
        
        # Requirement format: 'add_product', 'view_audit_logs', etc.
        required_codename = f"{required_base}_{model_name}"
        
        # Check if the role has this permission
        return user_role.permissions.filter(codename=required_codename).exists()
