from tenants.infrastructure.protocols_control import IFeatureFlagProvider
from tenants.infrastructure.utils.context import get_current_tenant
import logging

logger = logging.getLogger(__name__)

class DatabaseFlagProvider(IFeatureFlagProvider):
    """
    Tier 66: Cost-Effective Feature Flags.
    Stores flags in the Tenant.config JSONField under 'features'.
    No extra DB hits if tenant is already in context.
    """
    def is_enabled(self, feature_key, tenant_id, default=False, **kwargs):
        # We assume context has the tenant populated
        tenant = get_current_tenant()
        if not tenant or str(tenant.id) != str(tenant_id):
            # Fallback or fetch if needed (skipping fetch for perf in this demo)
            return default
            
        features = tenant.config.get('features', {})
        return features.get(feature_key, default)

    def get_all_flags(self, tenant_id):
        tenant = get_current_tenant()
        if not tenant:
            return {}
        return tenant.config.get('features', {})

class LaunchDarklyProvider(IFeatureFlagProvider):
    """
    Tier 66: Enterprise Feature Flags.
    """
    def __init__(self, config=None):
        self.config = config or {}
        self.sdk_key = self.config.get('sdk_key')
        
    def is_enabled(self, feature_key, tenant_id, default=False, **kwargs):
        # Mocking LD Client
        # ld_client.variation(feature_key, {"key": tenant_id}, default)
        logger.info(f"[LaunchDarkly] Checking {feature_key} for {tenant_id}")
        return default

    def get_all_flags(self, tenant_id):
        return {}
