# 🗺️ Sovereign Engine: Project Navigation Map

This map provides a high-fidelity overview of the project's distributed architecture, mapping business domains to their corresponding code locations and API endpoints.

## 🏛️ The 4-Layer Architecture
The system follows a strict **Clean Architecture** to ensure vendor-agnosticism and multi-tenant sovereignty.

| Layer | Responsibility | Directory |
| :--- | :--- | :--- |
| **Interface** | API Endpoints, Serializers, Routing | `tenants/api/` |
| **Application** | Use Cases, Services, Business Orchestration | `tenants/business/` |
| **Domain** | Core Models, Invariants, Entities | `tenants/domain/` |
| **Infrastructure** | Adapters, Protocols, Cloud Hubs, Utilities | `tenants/infrastructure/` |

---

## 🧭 Domain-to-API Mapping
Find the logic for a specific feature by following its domain folder.

| Domain | Interface (Views) | Path Prefix (`/api/v1/...`) |
| :--- | :--- | :--- |
| **Identity & Access** | `views_identity.py` | `/auth/`, `/roles/`, `/permissions/` |
| **Communication** | `views_communication.py` | `/communication/` (Email, SMS, WhatsApp) |
| **Onboarding** | `views_onboarding.py` | `/onboard/` |
| **Governance** | `views_governance.py` | `/quotas/`, `/audit-logs/` |
| **Infrastructure** | `views_infrastructure.py` | `/domains/`, `/search/`, `/health/` |
| **Collaboration** | `views_collaboration.py` | `/invites/`, `/members/` |
| **Intelligence (AI)** | `views_intelligence.py` | `/intelligence/` |
| **Settings** | `views_settings.py` | `/settings/` |

---

## ⚡ The Control Centers
Critical "Junction Files" that tie the distributed system together.

1.  **Central Router**: `tenants/urls.py` — The single source of truth for all API registrations.
2.  **Infrastructure Hub**: `tenants/infrastructure/hub.py` — The unified gateway to all cloud providers (S3, Stripe, Twilio, etc.).
3.  **Cross-App Registry**: `tenants/infrastructure/registry.py` — Allows external apps to register APIs/Search without touching core code.
4.  **Resilience Core**: `tenants/infrastructure/utils/resilience.py` — The home of the Sovereign Circuit Breaker.

---

## 🛠️ Developer Tooling
Use these derived assets for 100% visibility:
- **Consumer Map**: [sovereign_postman_collection.json](file:///home/mohanraj/projects/multi-tenant/sovereign_postman_collection.json)
- **Live Specs**: `/api/docs/swagger/` (Local Host)
- **Architectural Plan**: [implementation_plan.md](file:///home/mohanraj/.gemini/antigravity/brain/a5b0c19c-803b-49f4-9687-1c6cef1c8675/implementation_plan.md)

🥂🚀🏛️ **Every folder is a specialized island. Use this map to navigate the sovereign archipelago.**
