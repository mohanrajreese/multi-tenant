import os
import uuid

def tenant_path(instance, filename):
    """
    Generates a secure path for tenant uploads.
    Structure: tenants/{tenant_id}/{uuid}{ext}
    """
    ext = filename.split('.')[-1]
    new_filename = f"{uuid.uuid4()}.{ext}"
    return f"tenants/{instance.id}/assets/{new_filename}"

def tenant_file_path(instance, filename):
    """
    Alias for tenant_path, used in some migrations.
    """
    return tenant_path(instance, filename)
