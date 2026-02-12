# 🦅 Sovereign Engine: Integration Blueprint

The `tenants` app in this project is designed as a **Sovereign Engine**. It is project-agnostic and can be "plugged" into any new Django project to instantly provide 27-tier multi-tenancy.

## 📦 Quick Start: Plugging into a New Project

### 1. Copy the Engine
Copy the `tenants/` folder into your new Django project directory.

### 2. Update `settings.py`
Add the core engine components to your configuration:

```python
INSTALLED_APPS = [
    ...,
    'tenants.apps.TenantsConfig',  # The Engine
    'rest_framework',
    'rest_framework.authtoken',
]

MIDDLEWARE = [
    'tenants.middleware.middleware.TenantResolutionMiddleware',  # Context Resolver
    'tenants.middleware.middleware.TenantSecurityMiddleware',    # Guards
    'django.middleware.common.CommonMiddleware',
    ...,
    'tenants.middleware.middleware_user.UserContextMiddleware',   # User Context
]

# Configure the Database Router for Physical Isolation support
DATABASE_ROUTERS = ['tenants.infrastructure.database.routing.TenantRouter']

# Register the Global Exception Handler
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'tenants.api.exceptions_handler.sovereign_exception_handler',
    ...
}
```

### 3. Make your Models "Tenant-Aware"
In any app (e.g., `inventory`), simply inherit from `TenantAwareModel`:

```python
from tenants.models import TenantAwareModel

class Widget(TenantAwareModel):
    name = models.CharField(max_length=100)
    # No need to add tenant field, it's automatic!
```

### 4. Plug into the API
The engine automatically discovers your APIs if you register them:

```python
# inventory/apps.py
from tenants.infrastructure.registry import APIRegistry

class InventoryConfig(AppConfig):
    name = 'inventory'

    def ready(self):
        from .api import WidgetViewSet
        APIRegistry.register(r'widgets', WidgetViewSet, basename='widget')
```

## 🛠️ Advanced Hooks
- **Hybrid Isolation**: Set `isolation_mode` to `PHYSICAL` on any Tenant to instantly switch them to a private PostgreSQL schema.
- **Observability**: Add the `TenantContextFilter` to your logging config to get organization-tagged logs.
- **Provider Agnostic**: Swap Email/Storage/SSO providers via the `Tenant` config JSON fields without changing code.

---
**Your new project is now a Sovereign Cloud Platform.** 🥂🚀
