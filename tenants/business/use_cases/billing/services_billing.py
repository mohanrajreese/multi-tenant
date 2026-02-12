from tenants.models import Tenant
from .factory import BillingFactory

class BillingPortalService:
    """
    Omega Tier: Enterprise Self-Service Billing.
    Generates secure links for tenants to manage their own subscriptions.
    """
    
    @staticmethod
    def get_management_link(tenant: Tenant, return_url: str) -> str:
        """
        Returns a URL for the tenant to manage their billing/invoices.
        The URL is provider-specific (Stripe vs Paddle).
        """
        provider = BillingFactory.get_provider(tenant)
        return provider.get_portal_url(tenant, return_url)

    @staticmethod
    def sync_subscription_status(tenant: Tenant, status: str):
        """
        Updates the tenant's internal status based on provider events.
        """
        tenant.subscription_status = status
        
        if status == 'active':
            tenant.is_active = True
        elif status == 'canceled':
            tenant.is_active = False
            print(f"[SECURITY] Tenant {tenant.slug} SUSPENDED: Subscription Canceled.")
            
        tenant.save()

    @staticmethod
    def handle_payment_failure(tenant: Tenant):
        """
        Omega Tier: Grace Period Logic.
        Instead of immediate suspension, we flag the tenant as past_due.
        A background cron would check 'updated_at' to suspend after 3 days.
        """
        tenant.subscription_status = 'past_due'
        # In a real setup, we would send a 'PaymentFailed' domain event
        # which triggers the EmailService to warn the customer.
        tenant.save()
        print(f"[BILLING] Tenant {tenant.slug} entered GRACE PERIOD (past_due).")
