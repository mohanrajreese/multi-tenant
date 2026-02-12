import logging
from tenants.models.models_billing import Entitlement
from tenants.infrastructure.utils import get_current_tenant

logger = logging.getLogger(__name__)

class EntitlementsEngine:
    """
    High-speed feature-gating engine for Enterprise tiers.
    """
    
    @staticmethod
    def has_access(feature_code: str) -> bool:
        """
        Checks if the current active tenant has access to a specific feature.
        """
        tenant = get_current_tenant()
        if not tenant:
            return False
            
        # In production, this would be heavily cached using TenantCache
        return Entitlement.objects.filter(
            tenant=tenant,
            feature_code=feature_code,
            is_enabled=True
        ).exists()

    @staticmethod
    def grant_feature(tenant, feature_code: str, metadata: dict = None):
        """Grant a feature to a tenant."""
        Entitlement.objects.update_or_create(
            tenant=tenant,
            feature_code=feature_code,
            defaults={'is_enabled': True, 'metadata': metadata or {}}
        )
