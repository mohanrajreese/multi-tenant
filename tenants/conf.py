from django.conf import settings
from typing import Any

class SovereignConfig:
    """
    SoC: Internal Configuration Hub.
    Centralizes all engine defaults and overrides with SOVEREIGN_ prefixing.
    """
    PREFIX = 'TENANT_' # Keeping TENANT_ prefix for backward compatibility with existing settings

    DEFAULTS = {
        'BASE_SAAS_DOMAIN': 'localhost',
        'MANAGED_APPS': ['tenants'],
        'STORAGE_PATH_PREFIX': 'tenants',
        'DEFAULT_ISOLATION': 'LOGICAL',
        'MIGRATION_PARALLELISM': 4,
        'QUOTA_STRICT_MODE': True,
        'BILLING_PROVIDER_DEFAULT': 'stripe',
        'AUDIT_LOG_RETENTION_DAYS': 90,
    }

    def __getattr__(self, name: str) -> Any:
        if name not in self.DEFAULTS:
            raise AttributeError(f"Setting '{name}' is not part of the Sovereign Engine.")
        
        return getattr(settings, f"{self.PREFIX}{name}", self.DEFAULTS[name])

# Canonical instance for internal use
conf = SovereignConfig()
