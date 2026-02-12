import os
from .conf import conf

def tenant_path(instance, filename):
    """
    Generates a storage path scoped to the tenant.
    Format: tenants/{tenant_uuid}/{model_name}/{filename}
    """
    # 1. Determine the tenant ID
    tenant_id = None
    if hasattr(instance, 'tenant_id'):
        tenant_id = instance.tenant_id
    elif instance.__class__.__name__ == 'Tenant':
        tenant_id = instance.id
    
    # 2. Extract model name
    model_name = instance._meta.model_name
    
    # 3. Build path
    if tenant_id:
        return os.path.join(
            conf.STORAGE_PATH_PREFIX, 
            str(tenant_id), 
            model_name, 
            filename
        )
    
    # Fallback to general storage
    return os.path.join('general', model_name, filename)
