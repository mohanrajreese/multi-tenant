from django.contrib import admin
from tenants.infrastructure.utils import get_current_tenant

class TenantAdminMixin:
    """
    Mixin for ModelAdmin subclasses to enforce tenant isolation in the Django Admin.
    """
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        tenant = getattr(request, 'tenant', None)
        if tenant:
             # If the model is tenant-aware, it already uses TenantManager
             # But we can be explicit here to ensure admin isolation
             if hasattr(qs.model, 'tenant'):
                 return qs.filter(tenant=tenant)
        return qs

    def save_model(self, request, obj, form, change):
        if not change and not getattr(obj, 'tenant', None):
            tenant = getattr(request, 'tenant', None)
            if tenant:
                obj.tenant = tenant
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Filters foreign key choices to only show objects belonging to the current tenant.
        """
        tenant = getattr(request, 'tenant', None)
        if tenant and hasattr(db_field.remote_field.model, 'tenant'):
            kwargs["queryset"] = db_field.remote_field.model.objects.filter(tenant=tenant)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """
        Filters M2M choices to only show objects belonging to the current tenant.
        """
        tenant = getattr(request, 'tenant', None)
        if tenant and hasattr(db_field.remote_field.model, 'tenant'):
            kwargs["queryset"] = db_field.remote_field.model.objects.filter(tenant=tenant)
        return super().formfield_for_manytomany(db_field, request, **kwargs)
