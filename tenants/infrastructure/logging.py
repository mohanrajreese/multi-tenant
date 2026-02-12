import logging
from tenants.infrastructure.utils import get_current_tenant
from django.conf import settings

class TenantContextFilter(logging.Filter):
    """
    Zenith Tier: Distributed Tracing Filter.
    Injects tenant_id and user_id into every log record.
    """
    def filter(self, record):
        tenant = get_current_tenant()
        
        # Inject context metadata
        record.tenant_id = str(tenant.id) if tenant else "system"
        record.tenant_name = tenant.name if tenant else "system"
        
        # In a real-world scenario, we'd also pull the user from a ContextVar
        # For now, we defaults to "anonymous" if not available
        record.user_id = getattr(record, 'user_id', 'anonymous')
        
        return True
