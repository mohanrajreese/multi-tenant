from django.db import models

class TenantUserMixin:
    """
    Mixin for Custom User models to enable tenant-aware permission checks.
    """
    def has_tenant_permission(self, tenant, perm_codename):
        """
        Check if the user has a specific permission within a specific tenant context.
        """
        # Look up the user's membership for this tenant
        # Use .memberships (related_name on Membership model)
        membership = self.memberships.filter(tenant=tenant, is_active=True).select_related('role').first()
        
        if not membership or not membership.role:
            return False
            
        # Check if the role has the permission
        return membership.role.permissions.filter(codename=perm_codename).exists()
