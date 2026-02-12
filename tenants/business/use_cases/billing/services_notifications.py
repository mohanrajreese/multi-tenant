import logging
from django.core import signing
from django.urls import reverse
from django.conf import settings
from tenants.domain.models import Tenant
from tenants.infrastructure.adapters.communication.factory import CommunicationFactory

logger = logging.getLogger(__name__)

class BillingNotificationService:
    """
    Tau Tier: Secure Multi-Channel Billing Notifications.
    Sends payment links via Email and SMS with signed tokens for security.
    """

    @staticmethod
    def generate_secure_payment_link(tenant: Tenant, user_id: str) -> str:
        """
        Generates a secure, time-bound, signed link for the payment portal.
        """
        # Sign the tenant_id and user_id with a salt
        token = signing.dumps({'t': str(tenant.id), 'u': user_id}, salt='billing.secure')
        
        # In a real setup, this would be a URL to your frontend or a portal redirector
        base_url = f"https://{tenant.domains.filter(is_primary=True).first().domain or 'localhost'}"
        return f"{base_url}/billing/portal/?token={token}"

    @staticmethod
    def notify_payment_required(tenant: Tenant, user, channels=['email', 'sms']):
        """
        Orchestrates multi-channel notification.
        """
        payment_link = BillingNotificationService.generate_secure_payment_link(tenant, str(user.id))
        
        context = {
            'tenant_name': tenant.name,
            'payment_link': payment_link,
            'support_email': tenant.support_email
        }

        # 1. Send via Email
        if 'email' in channels:
            email_provider = CommunicationFactory.get_email_provider(tenant)
            try:
                email_provider.send_email(
                    to_email=user.email,
                    subject=f"Action Required: Payment for {tenant.name}",
                    template_name="billing_required",
                    context=context
                )
                logger.info(f"Payment notification EMAIL sent to {user.email}")
            except Exception as e:
                logger.error(f"Failed to send billing email: {e}")

        # 2. Send via SMS
        if 'sms' in channels and hasattr(user, 'phone_number') and user.phone_number:
            sms_provider = CommunicationFactory.get_sms_provider(tenant)
            try:
                message = f"Your payment link for {tenant.name}: {payment_link}"
                sms_provider.send_sms(to_number=user.phone_number, message=message)
                logger.info(f"Payment notification SMS sent to {user.phone_number}")
            except Exception as e:
                logger.error(f"Failed to send billing SMS: {e}")
