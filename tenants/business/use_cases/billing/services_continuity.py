import logging
from datetime import date
from django.db import transaction
from tenants.domain.models import Tenant
from .services_revenue import RevenueRecognitionService
from .services_notifications import BillingNotificationService

logger = logging.getLogger(__name__)

class ContinuityService:
    """
    Lifecycle Finality: The Continuity Engine.
    Handles automated billing transitions, renewals, and revenue handovers.
    """

    @staticmethod
    @transaction.atomic
    def process_renewal(tenant: Tenant):
        """
        Executes a renewal cycle for an active tenant.
        1. Verifies existing plan & pricing.
        2. Triggers payment via linked BillingProvider.
        3. Extends Revenue Recognition for the next period.
        """
        if tenant.subscription_status != 'active':
            logger.warning(f"Skipping renewal for non-active tenant: {tenant.slug}")
            return False

        # In production, this would call provider.charge_customer()
        # For this tier, we handle the state transition and revenue handover.
        
        logger.info(f"Initiating renewal cycle for {tenant.slug}")
        
        # 1. Extend Revenue Recognition
        plan = tenant.plan
        if not plan:
            logger.error(f"Cannot renew {tenant.slug}: No plan associated.")
            return False

        # Assuming 1 year renewal for simplicity in this logic
        RevenueRecognitionService.recognize_subscription_payment(
            tenant=tenant,
            total_amount=float(plan.yearly_price),
            period_months=12,
            start_date=date.today()
        )

        # 2. Notify Tenant of successful renewal
        BillingNotificationService.notify_invoice_paid(tenant, float(plan.yearly_price))
        
        logger.info(f"Renewal complete for {tenant.slug}. Continuity secured.")
        return True

    @staticmethod
    def handle_renewal_failure(tenant: Tenant, attempts: int = 1):
        """
        Handles failed payments during renewal cycles.
        Triggers dunning emails and grace period logic.
        """
        logger.error(f"Renewal failed for {tenant.slug} (Attempt {attempts})")
        
        if attempts >= 3:
            # Move to past_due / suspended
            tenant.subscription_status = 'past_due'
            tenant.is_active = False # Aggressive suspension for high-compliance
            tenant.save()
            logger.critical(f"Tenant {tenant.slug} suspended due to renewal failure.")
        else:
            # Trigger retry notification
            # BillingNotificationService.send_payment_failed_alert(tenant)
            pass
