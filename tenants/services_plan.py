from django.db import transaction
from .models import Plan, Quota, Tenant

class PlanService:
    """
    Manages subscription tiers and synchronizes quotas.
    """

    @staticmethod
    @transaction.atomic
    def apply_plan_to_tenant(tenant, plan):
        """
        Updates a tenant's plan and synchronizes the Quota model.
        """
        # 1. Update the Tenant object
        tenant.plan = plan
        tenant.save()

        # 2. Sync Quotas from the Plan's default_quotas
        # default_quotas format: {"max_products": 100, "max_members": 5}
        for resource_name, limit_value in plan.default_quotas.items():
            quota, created = Quota.objects.get_or_create(
                tenant=tenant,
                resource_name=resource_name,
                defaults={'limit_value': limit_value}
            )
            
            if not created:
                quota.limit_value = limit_value
                quota.save()

        return f"Successfully applied plan '{plan.name}' to {tenant.name}."

    @staticmethod
    def get_available_plans():
        """
        Returns all active subscription plans.
        """
        return Plan.objects.filter(is_active=True).order_by('monthly_price')
