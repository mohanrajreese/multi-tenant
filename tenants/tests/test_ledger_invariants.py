
import os
import django
import pytest
from hypothesis import given, strategies as st
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from tenants.domain.models import Tenant, LedgerAccount
from tenants.business.use_cases.core.services_ledger import BookkeepingService

@pytest.mark.django_db
class TestLedgerInvariants:
    """
    Tier 75: Mathematical Verification of Ledger Invariants.
    """
    
    @given(amounts=st.lists(st.decimals(min_value=1, max_value=1000, places=2), min_size=1, max_size=10))
    def test_balance_summation_invariant(self, amounts):
        """
        Prove that Balance = Sum(Credits) - Sum(Debits).
        """
        # Create a fresh tenant for each hypothesis run
        tenant = Tenant.objects.create(name="Hypothesis Tenant", slug=f"hypo-{os.urandom(4).hex()}")
        
        expected_balance = Decimal('0.0000')
        
        for amount in amounts:
            # Credit
            BookkeepingService.process_transaction(
                tenant=tenant,
                account_type='CREDIT',
                amount=amount,
                entry_type='CREDIT',
                description="Hypothesis Deposit"
            )
            expected_balance += amount
            
            # Debit (if possible)
            debit_amt = amount / 2
            BookkeepingService.process_transaction(
                tenant=tenant,
                account_type='CREDIT',
                amount=debit_amt,
                entry_type='DEBIT',
                description="Hypothesis Withdrawal"
            )
            expected_balance -= debit_amt
            
        # Verify Invariant
        account = LedgerAccount.objects.get(tenant=tenant, account_type='CREDIT')
        assert account.balance == expected_balance, f"Mathematical Invariant Violation: {account.balance} != {expected_balance}"
        
        # Cleanup
        tenant.delete()

if __name__ == "__main__":
    # This script is designed to be run via pytest
    pass
