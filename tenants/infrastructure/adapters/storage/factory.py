from django.conf import settings
from .providers.local import LocalProvider
from .providers.s3 import S3Provider

class StorageFactory:
    """
    Tier 58: Storage Resolution Factory.
    Decouples business logic from physical storage location.
    """
    
    @staticmethod
    def get_provider(tenant=None):
        """
        Returns the configured storage provider.
        Priority:
        1. Tenant-specific override (e.g. Bank wants Azure)
        2. System-wide default from settings
        """
        # 1. System Defaults
        config = getattr(settings, 'SOVEREIGN_STORAGE', {})
        provider_type = config.get('provider', 'local')
        
        # 2. Tenant Override (if tenant passed and has config)
        if tenant and tenant.config.get('storage'):
            tenant_config = tenant.config.get('storage')
            provider_type = tenant_config.get('provider', provider_type)
            # Merge configs (Tenant config overrides system config)
            config = {**config, **tenant_config}

        if provider_type == 's3':
            return S3Provider(config)
        elif provider_type == 'gcs':
            # return GCSProvider(config)
            pass
            
        return LocalProvider(config)
