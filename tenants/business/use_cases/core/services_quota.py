from django.db import models
from tenants.domain.models import Quota
from django.core.exceptions import ValidationError

class QuotaService:
    """
    Core engine for tracking and enforcing SaaS usage limits.
    """
    
    @staticmethod
    def check_quota(tenant, resource_name, increment=1):
        """
        Verifies if a tenant (and its ancestors) has enough quota.
        Tier 98: Hierarchy Enforcement.
        """
        # Check self and all parents
        ancestors = tenant.get_ancestors(include_self=True)
        
        for org in ancestors:
            quota = Quota.objects.filter(tenant=org, resource_name=resource_name).first()
            if not quota:
                continue

            # 0 means blocked/restricted unless specified
            if quota.limit_value > 0:
                if quota.current_usage + increment > quota.limit_value:
                    entity = "Organization" if org == tenant else f"Parent Organization ({org.name})"
                    raise ValidationError(
                        f"Quota exceeded for '{resource_name}' at {entity} level. "
                        f"Limit: {quota.limit_value}, Current: {quota.current_usage}"
                    )
        return True

    @staticmethod
    def increment_usage(tenant, resource_name, amount=1):
        """
        Increments usage for the tenant and all its ancestors.
        """
        ancestors = tenant.get_ancestors(include_self=True)
        tenant_ids = [t.id for t in ancestors]
        
        Quota.objects.filter(tenant_id__in=tenant_ids, resource_name=resource_name).update(
            current_usage=models.F('current_usage') + amount
        )

    @staticmethod
    def decrement_usage(tenant, resource_name, amount=1):
        """
        Decrements usage for the tenant and all its ancestors.
        """
        ancestors = tenant.get_ancestors(include_self=True)
        tenant_ids = [t.id for t in ancestors]

        # Prevent negative usage? Usually fine to just subtract.
        Quota.objects.filter(tenant_id__in=tenant_ids, resource_name=resource_name).update(
            current_usage=models.F('current_usage') - amount
        )
