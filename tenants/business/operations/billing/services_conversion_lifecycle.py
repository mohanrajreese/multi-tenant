import logging
from datetime import date, timedelta
from django.db import transaction
from django.utils import timezone
from tenants.models import Tenant

logger = logging.getLogger(__name__)

class TrialConversionService:
    """
    Lifecycle Finality: Trial-to-Paid Conversion Orchestrator.
    Manages trial transitions and conversion escalations.
    """

    @staticmethod
    def check_trial_expiries():
        """
        Background task hook to identify and process expiring trials.
        """
        trialing_tenants = Tenant.objects.filter(subscription_status='trialing')
        
        # In production, trials might have a 'trial_end_date' field.
        # For our tier, we manage this via config metadata or created_at + 14 days.
        
        for tenant in trialing_tenants:
            # Mock check: Trial expires 14 days after creation
            trial_end = tenant.created_at + timedelta(days=14)
            
            if timezone.now() > trial_end:
                TrialConversionService.expire_trial(tenant)

    @staticmethod
    @transaction.atomic
    def expire_trial(tenant: Tenant):
        """
        Transitions a tenant from 'trialing' to 'expired' or 'deactivated'.
        """
        logger.info(f"Trial expired for {tenant.slug}. Initiating conversion flow.")
        
        # 1. Set Status
        tenant.subscription_status = 'canceled'
        tenant.is_active = False
        tenant.save()
        
        # 2. Alert the owner
        print(f"[CONVERSION] Sending trial-ended conversion email to {tenant.slug}")
        # BillingNotificationService.send_trial_ended_alert(tenant)

    @staticmethod
    def convert_to_paid(tenant: Tenant, plan_slug: str):
        """
        Converts a trialing or expired tenant to a paid plan.
        """
        from .services_plan import PlanService # Avoid circular
        from tenants.models import Plan
        
        plan = Plan.objects.get(slug=plan_slug)
        tenant.subscription_status = 'active'
        tenant.is_active = True
        tenant.plan = plan
        tenant.save()
        
        logger.info(f"Tenant {tenant.slug} converted to PAID plan: {plan.name}")
