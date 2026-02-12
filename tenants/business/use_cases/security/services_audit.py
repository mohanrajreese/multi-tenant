from django.forms.models import model_to_dict
from tenants.domain.models import AuditLog
from tenants.infrastructure.utils.context import get_current_user, get_current_tenant, get_current_impersonator

class AuditService:
    @staticmethod
    def log_action(instance, action, old_instance=None):
        """
        Logs a Create, Update, or Delete action.
        """
        user = get_current_user()
        tenant = get_current_tenant() or getattr(instance, 'tenant', None)
        impersonator = get_current_impersonator()
        
        if not tenant:
            return # Don't log if we can't attribute it to a tenant
            
        changes = {}
        if action == 'UPDATE' and old_instance:
            old_data = model_to_dict(old_instance)
            new_data = model_to_dict(instance)
            
            for field, value in new_data.items():
                if field in old_data and old_data[field] != value:
                    # Capture [old, new]
                    changes[field] = [str(old_data[field]), str(value)]
        elif action == 'CREATE':
            changes = {field: [None, str(value)] for field, value in model_to_dict(instance).items()}
        
        from tenants.infrastructure.adapters.audit.factory import AuditFactory
        
        provider = AuditFactory.get_provider(tenant)
        provider.log_event(
            tenant_id=str(tenant.id),
            actor_id=str(user.id) if user else 'system',
            action=action,
            target_model=instance.__class__.__name__,
            target_id=str(instance.pk),
            changes=changes,
            # Pass objects for DatabaseProvider optimization
            tenant=tenant,
            user=user,
            impersonator=impersonator,
            object_repr=str(instance)
        )
