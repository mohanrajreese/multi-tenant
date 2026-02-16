import logging
import json
from django.db import transaction
from django.db.models import F
from tenants.domain.models.models_ledger import LedgerAccount, LedgerEntry
from tenants.business.exceptions import BusinessLogicError
from django.conf import settings

logger = logging.getLogger(__name__)

class RedisLedgerAggregator:
    """
    Tier 92: Performance Sovereignty.
    Handles high-concurrency balance updates in memory (Redis) to avoid SQL row contention.
    Flushes to SQL asynchronously via Celery (Tier 92.b).
    """
    
    @staticmethod
    def _get_client():
        try:
            import redis
            # Pull Redis URL from settings or use default
            url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379/1')
            return redis.from_url(url)
        except ImportError:
            return None

    @classmethod
    def process_atomic_step(cls, tenant_id, account_type, amount, entry_type):
        """
        Increments/Decrements the balance in Redis and buffers the transaction.
        """
        client = cls._get_client()
        if not client:
            return False # Fallback to SQL-only
            
        balance_key = f"ledger:{tenant_id}:{account_type}:balance"
        buffer_key = f"ledger:{tenant_id}:buffer"
        
        # 1. Update Balance Atomically
        delta = amount if entry_type == 'CREDIT' else -amount
        new_balance = client.incrbyfloat(balance_key, delta)
        
        # 2. Buffer for async flushing
        tx_data = {
            'account_type': account_type,
            'amount': float(amount),
            'entry_type': entry_type,
            'timestamp': str(logging.Formatter().formatTime(logging.LogRecord("", 0, "", 0, "", (), None)))
        }
        client.lpush(buffer_key, json.dumps(tx_data))
        
        return new_balance

class BookkeepingService:
    """
    Tier 75: Financial Ledger (Service).
    Provides a high-level API for double-entry bookkeeping.
    Tier 92: Integrated with Redis Aggregator for high-concurrency.
    """
    
    @staticmethod
    def process_transaction(tenant, account_type, amount, entry_type, description="", reference_id="", metadata=None):
        """
        Atomically processes a debit or credit. 
        Uses Redis Aggregator if enabled for high-performance scale.
        """
        # Tier 92: Try Redis Aggregator first for "Credit Hold" logic
        use_aggregator = getattr(settings, 'TENANT_LEDGER_AGGREGATOR_ENABLED', False)
        
        if use_aggregator:
            new_val = RedisLedgerAggregator.process_atomic_step(tenant.id, account_type, amount, entry_type)
            if new_val is not False:
                logger.info(f"[LEDGER-AGGREGATED] {entry_type} for {tenant.slug}. New Mem-Balance: {new_val}")
                return None, new_val # We return None for entry as it's buffered for async creation

        # Fallback to standard SQL Atomicity (Tier 75)
        with transaction.atomic():
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
            
            logger.info(f"[LEDGER-SQL] {entry_type} of {amount} processed for {tenant.slug} ({account_type}). New Balance: {account.balance}")
            return entry, account.balance
