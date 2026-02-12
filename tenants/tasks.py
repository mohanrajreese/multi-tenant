from functools import wraps
from .models import Tenant
from .utils import set_current_tenant

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
