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
