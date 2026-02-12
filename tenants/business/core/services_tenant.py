import os
import shutil
from django.conf import settings
from django.db import transaction
from django.apps import apps
from tenants.models import Tenant, TenantAwareModel

class TenantService:
    """
    Business Tier: Tenant Lifecycle Management.
    """

    @classmethod
    @transaction.atomic
    def purge_tenant_data(cls, tenant):
        """
        Compliance: Fully delete a tenant and ALL associated data.
        """
        from tenants.infrastructure.conf import conf
        tenant_name = tenant.name
        tenant_id = str(tenant.id)
        
        tenant.delete()

        tenant_media_path = os.path.join(settings.MEDIA_ROOT, conf.STORAGE_PATH_PREFIX, tenant_id)
        if os.path.exists(tenant_media_path):
            shutil.rmtree(tenant_media_path)
            
        return f"Successfully purged all data and files for {tenant_name}."

    @classmethod
    def export_tenant_data(cls, tenant):
        """
        GDPR Portability: Export all tenant-specific data as a JSON dictionary.
        """
        export_data = {
            'tenant': {
                'name': tenant.name,
                'slug': tenant.slug,
                'config': tenant.config
            },
            'resources': {}
        }
        
        for model in apps.get_models():
            if issubclass(model, TenantAwareModel):
                if model.__name__ == 'AuditLog': continue
                
                rows = model.objects.filter(tenant=tenant)
                export_data['resources'][model._meta.label] = [
                    {f.name: str(getattr(row, f.name)) for f in model._meta.fields if f.name != 'tenant'}
                    for row in rows
                ]
                
        return export_data
