# 🏛️ Architecture

The Engine follows **Clean Architecture** principles, strictly separating Business Logic from Infrastructure.

## The Infrastructure Hub

The `InfrastructureHub` is the single entry point for all external capabilities.

```python
from tenants.infrastructure.hub import InfrastructureHub

# Fully Agnostic Operations
db = InfrastructureHub.database()
email = InfrastructureHub.email(tenant)
storage = InfrastructureHub.storage(tenant)
ai = InfrastructureHub.intelligence(tenant)
```

## Provider Protocols

| Domain | Protocol | Implementations |
| :--- | :--- | :--- |
| **Communication** | `IEmailProvider` | `SendGrid`, `SES`, `SMTP` |
| **Storage** | `IStorageProvider` | `S3`, `Local`, `Azure` |
| **Identity** | `IIdentityProvider` | `OIDC`, `SAML`, `Google` |
| **Intelligence** | `ILLMProvider` | `OpenAI`, `Anthropic`, `Ollama` |
| **Audit** | `IAuditProvider` | `Splunk`, `Datadog`, `Database` |
| **Search** | `ISearchProvider` | `Postgres`, `Elasticsearch` |
