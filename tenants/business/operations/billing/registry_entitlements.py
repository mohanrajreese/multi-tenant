import logging
from typing import Dict, Any
from tenants.models.models_billing import Entitlement
from tenants.infrastructure.utils import get_current_tenant

logger = logging.getLogger(__name__)

class EntitlementsRegistry:
    """
    Omega Tier: Enterprise Feature Entitlements Registry.
    Centralized check for both numeric quotas and qualitative functional 'Capabilties'.
    """
    
    _features: Dict[str, str] = {
        "advanced_analytics": "High-resolution data insights and custom reports.",
        "bulk_export": "Exporting thousands of records in a single batch.",
        "sso_auth": "Enterprise Single Sign-On (Okta, Azure AD, etc.).",
        "private_storage": "Dedicated physical storage bucket for the tenant.",
        "multi_region": "Data residency in specific physical regions (US/EU/APAC)."
    }

    @classmethod
    def get_all_features(cls):
        return cls._features

    @staticmethod
    def is_entitled(feature_code: str) -> bool:
        """
        Verifies if the current tenant has been granted a specific functional capability.
        """
        tenant = get_current_tenant()
        if not tenant:
            return False
            
        # 1. Platform Staff always have access (if applicable)
        # 2. Check the Entitlement model (granted per tenant)
        return Entitlement.objects.filter(
            tenant=tenant,
            feature_code=feature_code,
            is_enabled=True
        ).exists()

    @staticmethod
    def grant_feature(tenant, feature_code: str):
        """Standard method for granting entitlements during Plan upgrades."""
        if feature_code not in EntitlementsRegistry._features:
            logger.warning(f"Granting unknown feature: {feature_code}")
            
        Entitlement.objects.update_or_create(
            tenant=tenant,
            feature_code=feature_code,
            defaults={'is_enabled': True}
        )
