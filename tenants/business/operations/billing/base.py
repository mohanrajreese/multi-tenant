from typing import Protocol, runtime_checkable
from tenants.models import Tenant

@runtime_checkable
class BillingProvider(Protocol):
    """
    Omega Tier: Enterprise Billing Interface.
    Agnostic strategy for Monetization.
    """
    
    def create_customer(self, tenant: Tenant) -> str:
        """Creates a customer in the provider and returns the provider_customer_id."""
        ...

    def update_usage(self, tenant: Tenant, metric_name: str, quantity: int):
        """Pushes metered usage data to the provider for usage-based billing."""
        ...

    def get_portal_url(self, tenant: Tenant, return_url: str) -> str:
        """Generates a secure link to the provider's billing portal."""
        ...

    def handle_webhook(self, payload: dict, signature: str):
        """Processes incoming provider events (payments, failures, cancellations)."""
        ...
