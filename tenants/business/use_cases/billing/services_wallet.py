import logging
from decimal import Decimal
from django.db import transaction
from tenants.domain.models import Tenant
from tenants.domain.models.models_billing import TenantCreditWallet

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

        # Chi Tier Refinement: Low Balance Alert
        previous_balance = wallet.balance
        wallet.spent_credits += credits_dec
        wallet.save()
        
        # Trigger alert if balance falls below 10% of total or a threshold
        if wallet.balance < (wallet.total_credits * Decimal("0.10")) and previous_balance >= (wallet.total_credits * Decimal("0.10")):
            from .services_notifications import BillingNotificationService
            from users.models import User # Assuming User model location
            # Notify the primary admin or tenant owner
            owner = Membership.objects.filter(tenant=tenant, role__name='Admin').first().user
            if owner:
                 # In production, use a specialized 'low_balance' template
                 print(f"[ALERT] Low balance for {tenant.slug}: {wallet.balance} credits remaining.")
        
        # Internal hook: Log the consumption event if needed
        logger.info(f"Deducted {credits_to_deduct} credits from {tenant.slug}. Remaining: {wallet.balance}")
        return True
