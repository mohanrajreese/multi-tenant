from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import TenantAwareModel, AuditLog
from .services_audit import AuditService

@receiver(pre_save)
def audit_pre_save(sender, instance, **kwargs):
    if not isinstance(instance, TenantAwareModel) or isinstance(instance, AuditLog):
        return
    
    if instance.pk:
        # It's an update. Capture the old instance.
        try:
            instance._old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            instance._old_instance = None
    else:
        instance._old_instance = None

@receiver(post_save)
def audit_post_save(sender, instance, created, **kwargs):
    if not isinstance(instance, TenantAwareModel) or isinstance(instance, AuditLog):
        return
    
    action = 'CREATE' if created else 'UPDATE'
    old_instance = getattr(instance, '_old_instance', None)
    
    AuditService.log_action(instance, action, old_instance)

@receiver(post_delete)
def audit_post_delete(sender, instance, **kwargs):
    if not isinstance(instance, TenantAwareModel) or isinstance(instance, AuditLog):
        return
    
    AuditService.log_action(instance, 'DELETE')

@receiver(post_delete)
def quota_post_delete(sender, instance, **kwargs):
    """
    Automated Quota Cleanup: Decrement usage when a resource is deleted.
    Assumes naming convention 'max_{model_name}s' (e.g., 'max_products').
    """
    if not isinstance(instance, TenantAwareModel) or isinstance(instance, AuditLog):
        return
    
    from .services_quota import QuotaService
    resource_name = f"max_{instance._meta.model_name}s"
    
    try:
        QuotaService.decrement_usage(instance.tenant, resource_name)
    except:
        # If no quota exists for this resource, it's a no-op
        pass
