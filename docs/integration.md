# 🔌 Integration Guide: Building a Sovereign SaaS

This guide explains how to integrate the **Sovereign Engine** (`tenants` app) into a new Django project and configure it for production.

## 🚀 Part 1: Quick Start (The "Plug-In")

### 1. Installation

Copy the `tenants/` directory into your project root. Then, add it to your `INSTALLED_APPS`:

```python
# settings.py

INSTALLED_APPS = [
    # ... django apps ...
    'rest_framework',
    'rest_framework.authtoken',
    'drf_spectacular',  # Optional: For API Docs
    
    # The Engine
    'tenants.apps.TenantsConfig',
]
```

### 2. Middleware (The Guard)

Add the `TenantResolutionMiddleware` near the top of your `MIDDLEWARE` list. It intercepts every request and resolves the tenant context.

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    
    # [REQUIRED] Resolves tenant from Subdomain (acme.saas.com) or Header (X-Tenant-ID)
    'tenants.middleware.middleware.TenantResolutionMiddleware',
    
    # [REQUIRED] Ensures users only access their own tenant
    'tenants.middleware.middleware.TenantSecurityMiddleware',
    
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # ...
]
```

### 3. Database Routing (The Isolation)

Configure the router to support Physical Isolation (separate schemas/DBs).

```python
DATABASE_ROUTERS = ['tenants.infrastructure.database.routing.TenantRouter']
```

---

## 🏥 Part 2: Real-Life Scenario (Hospital SaaS)

Imagine you are building **MediCloud**, a SaaS for hospitals. Each hospital needs strict data isolation.

### 1. Create a Tenant-Aware Model

Instead of `models.Model`, inherit from `TenantAwareModel`. The engine automatically injects a `tenant` ForeignKey and filters queries.

```python
# patients/models.py
from django.db import models
from tenants.models import TenantAwareModel

class PatientRecord(TenantAwareModel):
    name = models.CharField(max_length=100)
    diagnosis = models.TextField()
    
    # 'tenant' field is added automatically!
```

### 2. Register the API

You don't need to manually wire up URLs. Use the `APIRegistry`.

```python
# patients/apps.py
from django.apps import AppConfig
from tenants.infrastructure.registry import APIRegistry

class PatientsConfig(AppConfig):
    name = 'patients'

    def ready(self):
        from .api import PatientViewSet
        # Automatically mounts at /api/v1/patients/
        APIRegistry.register(r'patients', PatientViewSet, basename='patient')
```

### 3. Use Sovereign Infrastructure

Do **not** use `boto3` or `open()` directly. Use the Hub to support any hospital's infrastructure preference.

```python
# patients/views.py
from tenants.infrastructure.hub import InfrastructureHub

def upload_xray(request, tenant_id):
    tenant = request.tenant
    file = request.FILES['xray']
    
    # Saves to S3 (if AWS hospital) or Local Disk (if On-Prem hospital)
    # The code doesn't care!
    url = InfrastructureHub.storage(tenant).save(f"xrays/{file.name}", file)
    
    return JsonResponse({'url': url})
```

---

## ⚙️ Part 3: Configuration Examples

The engine is controlled via the `Tenant.config` JSON field.

### Scenario A: The "AWS Native" Startup
For tenants hosted on your AWS infrastructure.

```json
{
    "communication": {
        "email": { "provider": "ses", "region": "us-east-1" },
        "sms": { "provider": "twilio", "account_sid": "..." }
    },
    "storage": {
        "provider": "s3", 
        "bucket": "medicloud-production"
    },
    "intelligence": {
        "provider": "openai",
        "model": "gpt-4-turbo",
        "api_key": "sk-..."
    },
    "audit": {
        "provider": "datadog",
        "api_key": "..."
    }
}
```

### Scenario B: The "Enterprise On-Prem" Bank
For a bank that demands all data stay on their private servers.

```json
{
    "communication": {
        "email": { "provider": "smtp", "host": "mail.bank.com", "port": 587 }
    },
    "storage": {
        "provider": "local", 
        "base_path": "/mnt/secure_storage"
    },
    "intelligence": {
        "provider": "ollama",
        "base_url": "http://internal-ai:11434",
        "model": "llama3"
    },
    "audit": {
        "provider": "splunk",
        "host": "https://splunk.bank.com",
        "token": "..."
    }
}
```

---

## 🎓 Advanced Topics

*   **Hybrid Isolation**: Set `isolation_mode='PHYSICAL'` on a Tenant to move them from the shared schema to a dedicated Postgres schema instantly.
*   **Search**: Use `InfrastructureHub.search(tenant).search("query")` to search across all registered models using Postgres FTS or Elasticsearch.
*   **Docs**: Visit `/api/docs/swagger/` for the interactive API reference.
