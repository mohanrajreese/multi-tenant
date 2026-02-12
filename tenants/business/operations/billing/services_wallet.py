import logging
from decimal import Decimal
from django.db import transaction
from tenants.models import Tenant
from tenants.models.models_billing import TenantCreditWallet

logger = logging.getLogger(__name__)

class CreditWalletService:
    """
    Chi Tier: Pre-paid Credit & Drawdown Service.
    Manages the tenant's credit balance and real-time consumption.
    """

    @staticmethod
    def get_or_create_wallet(tenant: Tenant) -> TenantCreditWallet:
        wallet, _ = TenantCreditWallet.objects.get_or_create(tenant=tenant)
        return wallet

    @staticmethod
    def add_credits(tenant: Tenant, amount: float):
        """Adds credits to the tenant's wallet (e.g., after a purchase)."""
        wallet = CreditWalletService.get_or_create_wallet(tenant)
        wallet.total_credits += Decimal(str(amount))
        wallet.save()
        logger.info(f"Added {amount} credits to {tenant.slug}. New Balance: {wallet.balance}")

    @staticmethod
    @transaction.atomic
    def drawdown(tenant: Tenant, credits_to_deduct: float) -> bool:
        """
        Deducts credits from the wallet. Returns True if successful.
        """
        wallet = CreditWalletService.get_or_create_wallet(tenant)
        credits_dec = Decimal(str(credits_to_deduct))

        if wallet.balance < credits_dec:
            logger.warning(f"Insufficient credits for {tenant.slug}. Balance: {wallet.balance}, Requested: {credits_dec}")
            return False

        wallet.spent_credits += credits_dec
        wallet.save()
        
        # Internal hook: Log the consumption event if needed
        logger.info(f"Deducted {credits_to_deduct} credits from {tenant.slug}. Remaining: {wallet.balance}")
        return True
