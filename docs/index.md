# 🦅 Sovereign Engine

**The Vendor-Agnostic Multi-Tenant Engine for Django.**

The `tenants` app is a drop-in engine that transforms any Django project into a SaaS platform with **27-tier multi-tenancy**.

## 🚀 Key Features

*   **Infrastructure HUB**: Switch Providers (AWS, Google, Azure) via JSON config.
*   **Isolation Modes**: Toggle between `LOGICAL` (Shared DB) and `PHYSICAL` (Separate Schemas).
*   **Sovereign Identity**: Built-in SSO (OIDC, SAML, Google).
*   **Compliance**: Audit logging to Splunk, Datadog, or Database.

## 📦 Quick Start

```bash
pip install -r requirements.txt
python manage.py migrate_schemas
python manage.py runserver
```

Explore the [Architecture](architecture.md) or check the [Integration Guide](integration.md).
