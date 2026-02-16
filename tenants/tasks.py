from functools import wraps
from .models import Tenant
from .infrastructure.utils import set_current_tenant

def tenant_context_task(func):
    """
    Decorator for Celery/background tasks to automatically set the tenant context.
    Pass 'tenant_id' as a keyword argument to the task.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        tenant_id = kwargs.get('tenant_id')
        if tenant_id:
            try:
                tenant = Tenant.objects.get(id=tenant_id)
                set_current_tenant(tenant)
            except Tenant.DoesNotExist:
                pass
        
        try:
            return func(*args, **kwargs)
        finally:
            set_current_tenant(None)
            
    return wrapper

# Note: In a real Celery environment, these would be @shared_task
# For this architectural demonstration, we define them as callable logic
# that can be offloaded.

@tenant_context_task
def async_log_audit(model_label, object_id, action, old_data=None, tenant_id=None, impersonator_id=None):
    """Offloaded audit logging."""
    from django.apps import apps
    from django.contrib.auth import get_user_model
    from .business.use_cases.security.services_audit import AuditService
    from .infrastructure.utils import set_current_impersonator
    
    # Restore impersonator context for the audit logic
    if impersonator_id:
        User = get_user_model()
        try:
            impersonator = User.objects.get(id=impersonator_id)
            set_current_impersonator(impersonator)
        except User.DoesNotExist:
            pass

    model = apps.get_model(model_label)
    try:
        instance = model.objects.get(pk=object_id)
        AuditService.log_action(instance, action, old_data)
    except model.DoesNotExist:
        pass
    finally:
        set_current_impersonator(None)

@tenant_context_task
def async_trigger_webhook(tenant_id, event_type, data):
    """Offloaded webhook dispatch."""
    from .business.use_cases.security.services_webhook import WebhookService
    from .models import Tenant
    tenant = Tenant.objects.get(id=tenant_id)
    WebhookService.trigger_event(tenant, event_type, data)


@tenant_context_task
def flush_ledger_buffer(tenant_id=None):
    """
    Tier 92: Ledger Persistence.
    Flushes buffered transactions from Redis to the SQL Ledger.
    Synchronizes the SQL account balance with the Redis truth.
    """
    import json
    from .business.use_cases.core.services_ledger import RedisLedgerAggregator
    from .domain.models.models_ledger import LedgerAccount, LedgerEntry
    from .models import Tenant
    
    tenant = Tenant.objects.get(id=tenant_id)
    client = RedisLedgerAggregator._get_client()
    if not client:
        return
        
    buffer_key = f"ledger:{tenant_id}:buffer"
    balance_key = f"ledger:{tenant_id}:any:balance" # In a real system, we iterate over account types
    
    # 1. Pop all buffered transactions
    transactions = []
    while True:
        data = client.rpop(buffer_key)
        if not data:
            break
        transactions.append(json.loads(data))
    
    if not transactions:
        return

    # 2. Persist to SQL in bulk
    with transaction.atomic():
        for tx in transactions:
            account, _ = LedgerAccount.objects.get_or_create(
                tenant=tenant,
                account_type=tx['account_type']
            )
            LedgerEntry.objects.create(
                account=account,
                entry_type=tx['entry_type'],
                amount=tx['amount'],
                description=f"Redis Flush: {tx.get('timestamp')}"
            )
            
            # Sync balance
            if tx['entry_type'] == 'CREDIT':
                account.balance += tx['amount']
            else:
                account.balance -= tx['amount']
            account.save()
            
    return len(transactions)

from django.db import transaction

@tenant_context_task
def cleanup_expired_data(tenant_id=None):
    """
    Tier 99: Compliance Sovereignty.
    Automated data retention policy enforcement (GDPR/HIPAA).
    """
    from django.utils import timezone
    from datetime import timedelta
    from tenants.infrastructure.conf import conf
    from tenants.domain.models import AuditLog, TelemetryEntry
    
    retention_days = conf.AUDIT_LOG_RETENTION_DAYS or 90
    cutoff_date = timezone.now() - timedelta(days=retention_days)
    
    # 1. Clean Audit Logs
    audit_count, _ = AuditLog.objects.filter(created_at__lt=cutoff_date).delete()
    
    # 2. Clean Telemetry
    # Telemetry might have a shorter retention, but defaulting to same for now
    telemetry_count, _ = TelemetryEntry.objects.filter(timestamp__lt=cutoff_date).delete()
    
    return f"Cleaned {audit_count} audit logs and {telemetry_count} telemetry entries."
