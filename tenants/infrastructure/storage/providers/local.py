from django.core.files.storage import FileSystemStorage
from tenants.infrastructure.utils import get_current_tenant

class TenantLocalFileSystemStorage(FileSystemStorage):
    """
    Standard Local Storage but can be scoped via configuration if needed.
    """
    def __init__(self, config=None, *args, **kwargs):
        config = config or {}
        # Allows per-tenant base directories if desired, though usually 
        # the pathing utility handles the silo.
        location = config.get('location')
        base_url = config.get('base_url')
        super().__init__(location=location, base_url=base_url, *args, **kwargs)
