import pytest
from decimal import Decimal
from hypothesis import given, strategies as st
from hypothesis.extra.django import TransactionTestCase
from django.core.exceptions import ValidationError
from tenants.domain.models import Tenant, Quota
from tenants.domain.models.models_billing import TenantCreditWallet
from tenants.business.use_cases.billing.core.services_wallet import CreditWalletService
from tenants.business.use_cases.core.services_quota import QuotaService

@pytest.mark.django_db
class TestSovereignProperties(TransactionTestCase):
    """
    Tier 72: Indestructibility Layer.
    Uses property-based testing to prove invariants in financial and resource logic.
    """

    def setUp(self):
        # TransactionTestCase is used to ensure DB isolation between iterations
        # Although hypothesis + TransactionTestCase can be slow, it's safer for stateful DB tests.
        try:
            self.tenant = Tenant.objects.get(slug="prop-test")
        except Tenant.DoesNotExist:
            self.tenant = Tenant.objects.create(name="Property Test Corp", slug="prop-test")

    @given(st.lists(st.floats(min_value=0.01, max_value=1000.0, allow_nan=False, allow_infinity=False), min_size=1, max_size=20))
    def test_wallet_balance_consistency(self, amounts):
        """
        Property: Balance must always be total_credits minus spent_credits.
        """
        # Fresh state for each iteration
        TenantCreditWallet.objects.filter(tenant=self.tenant).delete()
        
        expected_total = Decimal("0.0000")
        for amt in amounts:
            CreditWalletService.add_credits(self.tenant, amt)
            expected_total += Decimal(str(amt))
        
        wallet = CreditWalletService.get_or_create_wallet(self.tenant)
        assert wallet.total_credits == expected_total
        assert wallet.balance == expected_total

    @given(
        initial=st.floats(min_value=100.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        drawdown=st.floats(min_value=1000.1, max_value=2000.0, allow_nan=False, allow_infinity=False)
    )
    def test_overdraw_prevention(self, initial, drawdown):
        """
        Property: Drawdown MUST fail if balance is insufficient.
        """
        TenantCreditWallet.objects.filter(tenant=self.tenant).delete()
        CreditWalletService.add_credits(self.tenant, initial)
        
        success = CreditWalletService.drawdown(self.tenant, drawdown)
        assert success is False
        
        # Verify balance was not touched
        wallet = CreditWalletService.get_or_create_wallet(self.tenant)
        assert wallet.spent_credits == 0
        assert wallet.balance == Decimal(str(initial))

    @given(
        limit=st.integers(min_value=1, max_value=100),
        increments=st.lists(st.integers(min_value=1, max_value=5), max_size=30)
    )
    def test_quota_enforcement(self, limit, increments):
        """
        Property: Quota check must correctly reject increments that would exceed the limit.
        """
        resource = "api_calls"
        # Reset state
        Quota.objects.filter(tenant=self.tenant, resource_name=resource).delete()
        Quota.objects.create(tenant=self.tenant, resource_name=resource, limit_value=limit)
        
        usage = 0
        for inc in increments:
            try:
                # 1. Enforcement Check
                QuotaService.check_quota(self.tenant, resource, increment=inc)
                
                # 2. Logic Check: If we got here, it must be within limits
                assert usage + inc <= limit
                
                # 3. Apply Usage
                QuotaService.increment_usage(self.tenant, resource, amount=inc)
                usage += inc
                
                # Refresh from DB to verify update
                q = Quota.objects.get(tenant=self.tenant, resource_name=resource)
                assert q.current_usage == usage
            except ValidationError:
                # 4. Logic Check: If it failed, it must have exceeded the limit
                assert usage + inc > limit
                break
