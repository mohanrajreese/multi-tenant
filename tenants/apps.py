from django.apps import AppConfig

class TenantsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = "tenants"

    def ready(self):
        from . import signals
        from .infrastructure import checks # Ensure checks are registered
        from .infrastructure.registry import SearchRegistry
        from .infrastructure.utils.telemetry import setup_telemetry
        from .infrastructure.conf import conf
        from .models import Membership, AuditLog
        
        # 🛡️ Tier 80: Fail-Fast Startup Config Check
        conf.validate_startup()

        # 🛡️ Initialize Distributed Tracing
        setup_telemetry()

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
