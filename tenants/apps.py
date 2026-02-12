from django.apps import AppConfig

class TenantsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = "tenants"

    def ready(self):
        import tenants.signals
        from .registry import SearchRegistry
        from .models import Membership, AuditLog

        # Register internal models for search
        SearchRegistry.register(
            Membership, 
            ['user__email', 'role__name'],
            lambda m: {'id': m.id, 'email': m.user.email, 'role': m.role.name}
        )
        SearchRegistry.register(
            AuditLog,
            ['model_name', 'object_repr', 'user__email'],
            lambda l: {'id': l.id, 'action': l.action, 'model': l.model_name}
        )
