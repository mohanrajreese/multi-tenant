import logging
import uuid
from tenants.models import Tenant
from ..base import BillingProvider

logger = logging.getLogger(__name__)

class UPIProvider(BillingProvider):
    """
    Upsilon Tier: Localized UPI (Unified Payments Interface) Provider.
    Supports QR code generation and Intent-based mobile payments (e.g., Razorpay/Stripe India).
    """

    def create_customer(self, tenant: Tenant) -> str:
        return f"upi_cus_{tenant.slug[:10]}"

    def update_usage(self, tenant: Tenant, metric_name: str, quantity: int, currency: str = "INR"):
        """UPI is typically for one-time or fixed-price, but we support metered sync if the gateway allows."""
        print(f"[UPI] Syncing {quantity} {metric_name} in {currency}")

    def update_quantity(self, tenant: Tenant, quantity: int):
        print(f"[UPI] Updating seat count to {quantity}")

    def calculate_taxes(self, tenant: Tenant, amount: float) -> float:
        # standard GST for India
        return amount * 0.18

    def apply_coupon(self, tenant: Tenant, coupon_code: str) -> bool:
        print(f"[UPI] Applying localized coupon {coupon_code}")
        return True

    def generate_upi_qr(self, tenant: Tenant, amount: float, currency: str = "INR") -> str:
        """
        Generates a standard UPI QR string/link.
        """
        txn_id = uuid.uuid4().hex
        # Standard UPI format: upi://pay?pa=VPA&pn=NAME&am=AMOUNT&cu=CURR&tr=TXNID
        vpa = tenant.config.get('billing', {}).get('upi_vpa', 'merchant@bank')
        qr_string = f"upi://pay?pa={vpa}&pn={tenant.name}&am={amount}&cu={currency}&tr={txn_id}"
        logger.info(f"Generated UPI QR for {tenant.slug}: {qr_string}")
        return qr_string

    def get_portal_url(self, tenant: Tenant, return_url: str) -> str:
        return f"https://localized-gateway.com/pay/{tenant.id}?next={return_url}"
