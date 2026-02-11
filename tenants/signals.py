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
