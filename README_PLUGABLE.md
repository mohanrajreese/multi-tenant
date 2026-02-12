# Plug-and-Play Multi-Tenant Engine Guide

This guide explains how to integrate the `tenants` app into a clean Django project to instantly enable enterprise multi-tenancy.

## 1. Installation & Requirements
Copy the `tenants` directory into your new project. Ensure the following are installed:
```bash
poetry add djangorestframework drf-spectacular dnspython
```

## 2. Global Configuration (`settings.py`)

### App Registration
Add `tenants` and DRF components to your `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'rest_framework.authtoken',
    'drf_spectacular',
    'tenants',
]
```

### Middleware
The `TenantResolver` must run early to establish context:
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # ...
    'tenants.middleware.TenantResolverMiddleware', 
    'django.middleware.common.CommonMiddleware',
    # ...
]
```

### Engine Settings
Define which apps the engine should manage:
```python
TENANT_BASE_DOMAIN = 'localhost' # Your root domain
TENANT_MANAGED_APPS = ['tenants', 'your_app_name'] # Apps to include in Permission Discovery
```

## 3. Creating Tenant-Aware Models & Users

### The User Model
Your custom User model should inherit from `TenantUserMixin` to enable permission checks:
```python
from django.contrib.auth.models import AbstractUser
from tenants.mixins import TenantUserMixin

class User(AbstractUser, TenantUserMixin):
    # Your custom fields...
```

### Business Models
In your project-specific apps, inherit from `TenantAwareModel`:
```python
from tenants.models import TenantAwareModel

class YourModel(TenantAwareModel):
    name = models.CharField(max_length=100)
```

## 4. The SaaS Gold Standard (Premium Features)
This engine includes enterprise features that you can use out of the box:

### 🎨 Tenant Branding
The `Tenant` model now supports custom **Logos**, **Hex Colors**, and **Contact Info**. These fields are automatically exposed in the `TenantSerializer` and can be set during onboarding.

## 5. API Auto-Routing (Unified Gateway)
New apps can automatically join the global REST API tree. In your app's `ready()` method, register your ViewSet with the central registry:

```python
# your_app/apps.py
from tenants.registry import APIRegistry
from .api_views import YourViewSet

class YourConfig(AppConfig):
    def ready(self):
        APIRegistry.register(r'your-resource', YourViewSet, basename='your_api')
```

This makes your endpoint available at `/api/v1/your-resource/` instantly, with no URL changes required in the core project.

### 🛡️ Scoped File Storage
Never worry about data leakage in file uploads. The engine includes a `tenant_path` utility that automatically isolates files into tenant-specific buckets:
```python
from tenants.models import TenantAwareModel
from tenants.storage_utils import tenant_path

class Document(TenantAwareModel):
    file = models.FileField(upload_to=tenant_path) # 🚀 Isolated automatically
```

### ⚙️ Centralized Configuration
Modify the engine's behavior in your `settings.py` without touching the engine code:
- `TENANT_BASE_DOMAIN`: Your root SaaS domain.
- `TENANT_MANAGED_APPS`: Apps to include in RBAC/Search.
- `TENANT_STORAGE_PREFIX`: Root folder for isolated uploads (default: `tenants`).

## 5. Exposing the API & Dashboard
Simply include the `tenants.urls` in your project's `core/urls.py`. This one line enables the entire Dashboard, API (v1), and interactive documentation:

```python
# core/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('users.urls')),
    path('', include('tenants.urls')), # 🚀 The Magic Line
]
```

## 6. Day 1 Workflow (New Repository)
How this engine accelerates your development:

1.  **Minute 1**: Copy the `tenants` app folder into your new repository.
2.  **Minute 10**: Update `settings.py` (Middlewares, Managed Apps, Base Domain).
3.  **Minute 30**: Create your first business model (e.g., `Order`, `Task`) inheriting from `TenantAwareModel`.
4.  **Minute 60**: **Live.** You have 100% tenant isolation, a searchable API, a team invitation system, and auto-generated Swagger documentation.

## 7. Platinum Enterprise Features
Commercial-ready features for professional SaaS deployments:

### ⚡ Usage Quotas
Limit how many resources a tenant can create (e.g., Free vs. Pro tiers):
```python
from tenants.services_quota import QuotaService
QuotaService.check_quota(request.tenant, 'max_products') # Raises ValidationError if reached
```

### ❄️ Maintenance Mode
Instantly lockout a specific tenant for upgrades or billing issues via the `is_maintenance` Boolean. They will see a branded 503 response while your staff-level users can still access the dashboard.

### 📝 Dynamic Configuration
The `config` JSONField on the `Tenant` model allows you to store per-tenant preferences like Feature Flags or API Keys without changing the database schema.

### 🧹 GDPR Purge
Fully compliant data deletion with one call:
```python
TenantService.purge_tenant_data(tenant) # Hard deletes the tenant and all related data via CASCADE
```

---
**Your "Multi-Tenant Engine" is now fully operational in your new project!**
