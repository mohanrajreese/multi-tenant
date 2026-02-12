from typing import Protocol, runtime_checkable
from tenants.models import Tenant

@runtime_checkable
class BillingProvider(Protocol):
    """
    Omega Tier: Enterprise Billing Interface.
    Agnostic strategy for Monetization.
    """
    
    def create_customer(self, tenant: Tenant) -> str:
        """Creates a customer in the billing provider's system."""
        ...

    def update_usage(self, tenant: Tenant, metric_name: str, quantity: int, currency: str = "USD"):
        """Pushes metered usage data with currency awareness."""
        ...

    def update_quantity(self, tenant: Tenant, quantity: int):
        """Updates the subscription quantity (Seat-Based Billing)."""
        ...

    def calculate_taxes(self, tenant: Tenant, amount: float) -> float:
        """Calculates taxes for an amount based on tenant billing data."""
        ...

    def apply_coupon(self, tenant: Tenant, coupon_code: str) -> bool:
        """Applies a promotion code/coupon to a tenant's subscription."""
        ...

    def get_portal_url(self, tenant: Tenant, return_url: str) -> str:
        """Generates a secure link to the provider's billing portal."""
        ...

    def handle_webhook(self, payload: dict, signature: str):
        """Processes incoming provider events (payments, failures, cancellations)."""
        ...
