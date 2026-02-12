import logging
from tenants.models import Tenant

logger = logging.getLogger(__name__)

class BlueprintService:
    """
    Tier 49: Industry Blueprint Engine.
    Accelerates 'Time-to-Value' via domain-specific templates.
    """
    BLUEPRINTS = {
        'fintech': {
            'features': ['ledger', 'compliance_archival'],
            'config': {'security_level': 'high', 'auditing': 'verbose'}
        },
        'crm': {
            'features': ['bulk_email', 'contact_management'],
            'config': {'sync_frequency': 'hourly'}
        }
    }

    @staticmethod
    def apply_blueprint(tenant: Tenant, blueprint_key: str):
        """
        One-click initialization of the tenant ecosystem.
        """
        blueprint = BlueprintService.BLUEPRINTS.get(blueprint_key)
        if not blueprint:
            raise ValueError(f"Blueprint '{blueprint_key}' not found.")
        
        logger.info(f"Applying {blueprint_key} blueprint to {tenant.slug}")
        
        # 1. Apply Settings
        tenant.config.update(blueprint['config'])
        tenant.save()
        
        # 2. Auto-Grant features (via EntitlementsEngine)
        from .entitlements import EntitlementsEngine
        for feature in blueprint['features']:
            EntitlementsEngine.grant_feature(tenant, feature)
            
        return True
