import os
from uuid import uuid4

def tenant_file_path(instance, filename):
    """
    Generates a path for uploaded files: 
    tenants/<tenant_id>/<model_name>/<filename>
    """
    # Get the tenant ID from the instance
    tenant_id = str(instance.tenant.id)
    # Get the model name (e.g., 'product')
    model_name = instance.__class__.__name__.lower()
    
    # Optional: Rename file to a random UUID to prevent name collisions
    ext = filename.split('.')[-1]
    filename = f"{uuid4()}.{ext}"
    
    return os.path.join('tenants', tenant_id, model_name, filename)
