from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import TenantAwareModel, AuditLog
from .business.security.services_audit import AuditService
from .tasks import async_log_audit, async_trigger_webhook
import sys

# We skip offloading in tests to ensure assertions work correctly
IS_TESTING = 'test' in sys.argv

@receiver(pre_save)
def audit_pre_save(sender, instance, **kwargs):
    if not isinstance(instance, TenantAwareModel) or isinstance(instance, AuditLog):
        return
    
    if instance.pk:
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
    # We serialize the old instance if it exists for background processing
    old_data = None
    if not created and hasattr(instance, '_old_instance') and instance._old_instance:
        from django.core.serializers import serialize
        import json
        old_data = json.loads(serialize('json', [instance._old_instance]))[0]

    if IS_TESTING:
        AuditService.log_action(instance, action, instance._old_instance if not created else None)
    else:
        async_log_audit.delay(
            model_label=instance._meta.label,
            object_id=instance.pk,
            action=action,
            old_data=old_data,
            tenant_id=instance.tenant_id
        )

@receiver(post_delete)
def audit_post_delete(sender, instance, **kwargs):
    if not isinstance(instance, TenantAwareModel) or isinstance(instance, AuditLog):
        return
    
    if IS_TESTING:
        AuditService.log_action(instance, 'DELETE')
    else:
        async_log_audit.delay(
            model_label=instance._meta.label,
            object_id=instance.pk,
            action='DELETE',
            tenant_id=instance.tenant_id
        )

@receiver(post_delete)
def quota_post_delete(sender, instance, **kwargs):
    if not isinstance(instance, TenantAwareModel) or isinstance(instance, AuditLog):
        return
    
    # Quota decrement remains synchronous for high-consistency 
    # resource release, but we keep it fast.
    from .business.core.services_quota import QuotaService
    resource_name = f"max_{instance._meta.model_name}s"
    try:
        QuotaService.decrement_usage(instance.tenant, resource_name)
    except:
        pass

@receiver(post_save)
def automated_webhook_post_save(sender, instance, created, **kwargs):
    if not isinstance(instance, TenantAwareModel) or isinstance(instance, AuditLog):
        return
        
    event_prefix = instance._meta.model_name
    event_type = f"{event_prefix}.created" if created else f"{event_prefix}.updated"
    
    data = {
        'id': str(instance.pk),
        'repr': str(instance),
        'model': instance._meta.label
    }
    
    if IS_TESTING:
        from tenants.business.security.services_webhook import WebhookService
        WebhookService.trigger_event(instance.tenant, event_type, data)
    else:
        async_trigger_webhook.delay(
            tenant_id=instance.tenant_id,
            event_type=event_type,
            data=data
        )

@receiver(post_delete)
def automated_webhook_post_delete(sender, instance, **kwargs):
    if not isinstance(instance, TenantAwareModel) or isinstance(instance, AuditLog):
        return
        
    event_type = f"{instance._meta.model_name}.deleted"
    data = {'id': str(instance.pk), 'model': instance._meta.label}
    
    if IS_TESTING:
        from tenants.business.security.services_webhook import WebhookService
        WebhookService.trigger_event(instance.tenant, event_type, data)
    else:
        async_trigger_webhook.delay(
            tenant_id=instance.tenant_id,
            event_type=event_type,
            data=data
        )
