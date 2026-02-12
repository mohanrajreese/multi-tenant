from .providers.s3 import TenantAwareS3Storage
from .providers.local import TenantLocalFileSystemStorage
from django.core.files.storage import default_storage

class StorageFactory:
    """
    Registry for Multi-Cloud Storage Isolation.
    Returns the appropriate Django Storage instance based on tenant config.
    """
    
    @staticmethod
    def get_storage(tenant=None):
        """
        Dynamic Resolver. If no tenant is provided, it attempts to 
        resolve from the current request context.
        """
        from tenants.infrastructure.utils import get_current_tenant
        tenant = tenant or get_current_tenant()
        
        if not tenant:
            return default_storage
            
        # Check tenant configuration for specific storage requirements
        config = tenant.config.get('storage', {})
        provider_type = config.get('provider', 'local')
        
        if provider_type == 's3':
            return TenantAwareS3Storage(config)
        elif provider_type == 'local':
            return TenantLocalFileSystemStorage(config)
            
        # Fallback to local
        return TenantLocalFileSystemStorage(config)

def get_tenant_storage():
    """
    A helper for FileField(storage=...) to enable dynamic runtime resolution.
    """
    return StorageFactory.get_storage()
