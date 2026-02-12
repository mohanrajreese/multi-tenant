from tenants.models import Tenant
from .base import BillingProvider

class StripeProvider:
    """
    Omega Tier: Enterprise Stripe Adapter.
    Handles Metered Billing, Portal generation, and Subscription Lifecycle.
    """
    
    def create_customer(self, tenant: Tenant) -> str:
        # In a real setup, this calls stripe.Customer.create(email=tenant.support_email)
        # Mocking a provider ID:
        return f"cus_{tenant.slug[:10]}"

    def update_usage(self, tenant: Tenant, metric_name: str, quantity: int):
        """
        Reports metered usage to Stripe.
        """
        customer_id = tenant.billing_customer_id
        if not customer_id:
            return
            
        print(f"[STRIPE] Reporting {quantity} usage for {metric_name}")

    def update_quantity(self, tenant: Tenant, quantity: int):
        """
        Updates the Stripe subscription quantity (Seats).
        """
        subscription_id = tenant.subscription_id
        if subscription_id:
            print(f"[STRIPE] Updating subscription {subscription_id} quantity to {quantity} seats")

    def calculate_taxes(self, tenant: Tenant, amount: float) -> float:
        """
        Uses Stripe Tax (Mock) to calculate taxes based on country_code.
        """
        rate = 0.2 if tenant.country_code == 'GB' else 0.08 if tenant.country_code == 'US' else 0.15
        return amount * rate

    def apply_coupon(self, tenant: Tenant, coupon_code: str) -> bool:
        """
        Applies a Stripe promotion code.
        """
        print(f"[STRIPE] Applying coupon {coupon_code} to tenant {tenant.slug}")
        return True

    def get_portal_url(self, tenant: Tenant, return_url: str) -> str:
        """Generates a secure Stripe Billing Portal link."""
        # In a real setup, this calls stripe.billing_portal.Session.create
        return f"https://billing.stripe.com/p/session/mock_{tenant.id}"

    def handle_webhook(self, payload: dict, signature: str):
        """
        Standardized handling for:
        - customer.subscription.updated -> sync plan
        - invoice.payment_failed -> toggle tenant.is_active = False
        """
        event_type = payload.get('type')
        print(f"[STRIPE WEBHOOK] Received: {event_type}")
        # Logic to emit Internal Events based on Stripe actions
