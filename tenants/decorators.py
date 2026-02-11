from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

def tenant_permission_required(perm_codename):
    """
    Decorator for views that checks if a user has a specific tenant permission.
    Usage: @tenant_permission_required('view_product')
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # 1. Ensure a tenant is identified
            if not request.tenant:
                raise PermissionDenied("No tenant context found.")
            
            # 2. Check the permission
            if not request.user.is_authenticated:
                raise PermissionDenied("User is not authenticated.")
                
            if not request.user.has_tenant_permission(request.tenant, perm_codename):
                raise PermissionDenied(f"You do not have the '{perm_codename}' permission.")
                
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
