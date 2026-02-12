import os
from uuid import uuid4

def tenant_storage_path(instance, filename):
    """
    Sovereign Pathing: Standardized multi-tenant storage silos.
    Format: tenants/{tenant_id}/{model_name}/{unique_filename}
    """
    # 1. Identify the tenant ID
    tenant_id = None
    if hasattr(instance, 'tenant_id'):
        tenant_id = str(instance.tenant_id)
    elif hasattr(instance, 'tenant') and instance.tenant:
        tenant_id = str(instance.tenant.id)
    
    # 2. Extract model name for organization
    model_name = instance._meta.model_name
    
    # 3. Generate a unique filename to prevent collisions and directory traversal
    ext = filename.split('.')[-1]
    unique_name = f"{uuid4()}.{ext}"
    
    # 4. Build the final siloed path
    if tenant_id:
        return os.path.join('tenants', tenant_id, model_name, unique_name)
    
    # Fallback for tenant-less or shared data
    return os.path.join('general', model_name, unique_name)
