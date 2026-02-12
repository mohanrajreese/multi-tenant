import logging
from uuid import uuid4
from django.db import transaction
from tenants.models import Tenant
from .services_wallet import CreditWalletService

logger = logging.getLogger(__name__)

class ReferralEngine:
    """
    Tier 47: Product-Led Growth.
    Incentivized tenant-to-tenant referral loop.
    """

    @staticmethod
    def generate_referral_code(tenant: Tenant) -> str:
        """
        Generates or retrieves a unique referral code for the tenant.
        """
        code = tenant.config.get('referral_code')
        if not code:
            code = str(uuid4())[:8].upper()
            tenant.config['referral_code'] = code
            tenant.save()
        return code

    @staticmethod
    @transaction.atomic
    def process_referral_success(referred_tenant: Tenant, referrer_code: str):
        """
        Rewards the referrer when a new tenant signs up with their code.
        """
        referrer = Tenant.objects.filter(config__referral_code=referrer_code).first()
        if not referrer:
            logger.warning(f"Invalid referral code used: {referrer_code}")
            return False

        # In production, award 100 credits to the referrer
        reward_amount = 100.00
        CreditWalletService.top_up(referrer, reward_amount)
        
        # Link for tracking
        referred_tenant.config['referred_by'] = str(referrer.id)
        referred_tenant.save()
        
        logger.info(f"Referral Success: {referrer.slug} rewarded for inviting {referred_tenant.slug}")
        return True
