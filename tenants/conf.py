from django.conf import settings

class AppSettings:
    """
    Centralized configuration for the tenants app.
    Provides sensible defaults and easy access to project settings.
    """
    
    @property
    def BASE_SAAS_DOMAIN(self):
        return getattr(settings, 'TENANT_BASE_DOMAIN', 'localhost')

    @property
    def MANAGED_APPS(self):
        # Apps to include in Permission Discovery and Search by default
        return getattr(settings, 'TENANT_MANAGED_APPS', ['tenants'])

    @property
    def STORAGE_PATH_PREFIX(self):
        # Prefix for all tenant-scoped file uploads
        return getattr(settings, 'TENANT_STORAGE_PREFIX', 'tenants')

conf = AppSettings()
