import logging
from .utils import get_current_tenant
from .middleware_user import get_current_user

class TenantContextFilter(logging.Filter):
    """
    Apex Tier: Global Observability.
    Injects tenant_id and user_username into every log record automatically.
    """
    def filter(self, record):
        tenant = get_current_tenant()
        user = get_current_user()
        
        record.tenant_id = str(tenant.id) if tenant else "N/A"
        record.tenant_name = tenant.name if tenant else "N/A"
        record.user_id = str(user.id) if user and user.is_authenticated else "Anonymous"
        
        return True
