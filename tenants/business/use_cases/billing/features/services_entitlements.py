import logging
from tenants.domain.models.models_billing import Entitlement
from tenants.infrastructure.utils.context import get_current_tenant

logger = logging.getLogger(__name__)

class EntitlementsEngine:
    """
    High-speed feature-gating engine for Enterprise tiers.
    """
    
    @staticmethod
    def has_access(feature_code: str) -> bool:
        """
        Checks if the current active tenant has access to a feature.
        Logic order:
        1. Explicit Tenant Entitlement (Overrides Plan)
        2. Plan-level Default Entitlement
        """
        tenant = get_current_tenant()
        if not tenant:
            return False

        # 1. Check Explicit Tenant Entitlement
        ent = Entitlement.objects.filter(
            tenant=tenant,
            feature_code=feature_code
        ).first()

        if ent:
            return ent.is_valid()

        # 2. Inherit from Plan if exists
        if hasattr(tenant, 'plan') and tenant.plan:
            plan_ent = Entitlement.objects.filter(
                plan=tenant.plan,
                feature_code=feature_code
            ).first()
            if plan_ent:
                return plan_ent.is_valid()
            
        return False

    @staticmethod
    def grant_feature(tenant, feature_code: str, metadata: dict = None):
        """Grant a feature to a tenant."""
        Entitlement.objects.update_or_create(
            tenant=tenant,
            feature_code=feature_code,
            defaults={'is_enabled': True, 'metadata': metadata or {}}
        )
