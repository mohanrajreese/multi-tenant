
from django.db import transaction
from django.db.models import F
from tenants.domain.models.models_ledger import LedgerAccount, LedgerEntry
from tenants.business.exceptions import BusinessLogicError
import logging

logger = logging.getLogger(__name__)

class BookkeepingService:
    """
    Tier 75: Financial Ledger (Service).
    Provides a high-level API for double-entry bookkeeping.
    Ensures that balance updates and entry creation are atomic.
    """
    
    @staticmethod
    @transaction.atomic
    def process_transaction(tenant, account_type, amount, entry_type, description="", reference_id="", metadata=None):
        """
        Atomically processes a debit or credit against a tenant's ledger account.
        """
        # 1. Get or Create the ledger account
        account, created = LedgerAccount.objects.select_for_update().get_or_create(
            tenant=tenant,
            account_type=account_type,
            defaults={'name': f"{tenant.slug} {account_type.title()}"}
        )
        
        # 2. Validate sufficient funds for debits
        if entry_type == 'DEBIT' and account.balance < amount:
            raise BusinessLogicError(
                f"Insufficient funds in {account_type} account. Required: {amount}, Available: {account.balance}",
                code="INSUFFICIENT_FUNDS"
            )
            
        # 3. Create the ledger entry
        entry = LedgerEntry.objects.create(
            account=account,
            entry_type=entry_type,
            amount=amount,
            description=description,
            reference_id=reference_id,
            metadata=metadata or {}
        )
        
        # 4. Update the account balance
        if entry_type == 'CREDIT':
            account.balance += amount
        else:
            account.balance -= amount
            
        account.save()
        
        logger.info(f"[LEDGER] {entry_type} of {amount} processed for {tenant.slug} ({account_type}). New Balance: {account.balance}")
        return entry, account.balance
