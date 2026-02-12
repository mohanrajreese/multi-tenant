from django.core.checks import Error, register
from django.apps import apps
from django.conf import settings
from tenants.domain.models import TenantAwareModel

@register('deployment')
def check_tenant_isolation(app_configs, **kwargs):
    """
    Architectural Hardening: Soft Guard Protection.
    Ensures that all models in 'TENANT_MANAGED_APPS' inherit from TenantAwareModel.
    """
    errors = []
    # In production, this would be a setting. For now, we use a list of apps.
    managed_apps = getattr(settings, 'TENANT_MANAGED_APPS', ['products'])
    
    for app_label in managed_apps:
        try:
            app_config = apps.get_app_config(app_label)
            for model in app_config.get_models():
                if not issubclass(model, TenantAwareModel):
                    errors.append(
                        Error(
                            f"Model '{model._meta.label}' does not inherit from TenantAwareModel.",
                            hint="Ensure this model is tenant-isolated to prevent data leaks.",
                            obj=model,
                            id='tenants.E001',
                        )
                    )
        except LookupError:
            # App not found, skip
            pass
            
    return errors
