import logging
from tenants.models import Tenant

logger = logging.getLogger(__name__)

class MarketplaceRegistry:
    """
    Tier 47: Marketplace Sovereignty.
    Manages tenant-specific 'Extensions' or 'Apps'.
    """
    _EXTENSIONS = {
        'ai_copilot': {'name': 'AI Copilot', 'category': 'Productivity'},
        'bi_connector': {'name': 'BI Connector', 'category': 'Analytics'},
        'crm_sync': {'name': 'CRM Sync', 'category': 'Integration'},
    }

    @staticmethod
    def get_available_extensions():
        return MarketplaceRegistry._EXTENSIONS

    @staticmethod
    def enable_extension(tenant: Tenant, ext_key: str):
        """
        Enables an extension by updating the tenant's configuration.
        """
        if ext_key not in MarketplaceRegistry._EXTENSIONS:
            raise ValueError(f"Extension '{ext_key}' does not exist.")
        
        extensions = tenant.config.get('enabled_extensions', [])
        if ext_key not in extensions:
            extensions.append(ext_key)
            tenant.config['enabled_extensions'] = extensions
            tenant.save()
            logger.info(f"Extension '{ext_key}' enabled for {tenant.slug}")
        return True

    @staticmethod
    def is_enabled(tenant: Tenant, ext_key: str) -> bool:
        return ext_key in tenant.config.get('enabled_extensions', [])
