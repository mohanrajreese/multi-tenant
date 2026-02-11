# 📔 Exhaustive Technical Manual: Enterprise Multi-Tenant SaaS

This manual provides an in-depth, exhaustive explanation of every core feature implemented in this SaaS platform. It is designed for architects and developers who need to understand the "What", "Why", and "How" of the system.

---

## 1. Multi-Tenant Data Isolation (The "Vault" Pattern)

### 🔴 The Problem
In a shared database (Multi-Tenant), the biggest risk is **Data Leakage**. If a developer forgets a `.filter(tenant=...)` in a query, a user from "Apple" might accidentally see "Google's" data.

### 🟢 The Solution: Automated Isolation
We use a **Query Interceptor** pattern at the ORM level.

#### 🛠️ Implementation Details:
1.  **Global Context**: We use `threading.local` in `tenants/utils.py` to store the `tenant_id` for the current request. This acts as a global "vault" that is unique to each request.
2.  **Middleware**: `tenants/middleware.py` intercepts the incoming request, looks up the domain (e.g., `acme.localhost`), finds the `Tenant` object, and "sets" it in the global context.
3.  **Model Manager**: `tenants/models.py` defines a `TenantManager`. This manager overrides `get_queryset()` to automatically append `.filter(tenant=current_tenant)` to EVERY query.
4.  **Abstract Base Class**: Any model that needs isolation (like `Product`) inherits from `TenantAwareModel`.

#### 📂 Key Files:
- `tenants/utils.py`: Context storage.
- `tenants/middleware.py`: The identity resolver.
- `tenants/models.py`: The `TenantAwareModel` logic.

#### 🛡️ Security Check:
Even if a user tries to access `/products/5/` where ID 5 belongs to another tenant, the system will return a `404 Not Found` because the ORM query is pre-filtered to "Current Tenant Only."

---

## 2. Industry-Grade RBAC (Identity Silos)

### 🔴 The Problem
Traditional Django permissions are global. In SaaS, a user might be a "SuperAdmin" for their own company but shouldn't even exist in another company's records.

### 🟢 The Solution: Membership Pattern
We decouple the `User` from the `Tenant` using a middle-man: the `Membership`.

#### 🛠️ Implementation Details:
1.  **Membership Model**: Maps `User <-> Tenant <-> Role`.
2.  **Tenant-Scoped Roles**: The `Role` model itself is `TenantAware`. This means "Manager" for Apple can have different permissions than "Manager" for Google.
3.  **Decorator Logic**: The `tenant_permission_required` decorator in `tenants/decorators.py` doesn't check the global `user` permissions. Instead, it looks up the specific `Membership` for the current `request.tenant` and verifies the associated `Role`.

#### 📂 Key Files:
- `tenants/models.py`: `Role` and `Membership` definitions.
- `tenants/decorators.py`: The security enforcement logic.

---

## 3. Atomic Onboarding (The Orchestrator)

### 🔴 The Problem
Creating a new tenant involves multiple steps: creating the tenant record, the domain, the admin user, and the default roles. If step 3 fails, steps 1 and 2 are left as "garbage" in your DB.

### 🟢 The Solution: The Service Pattern
We use a centralized **Service Layer** with atomic transactions.

#### 🛠️ Implementation Details:
1.  **Onboarding Service**: `tenants/services.py` contains `onboard_tenant()`.
2.  **Atomicity**: Wrapped in `@transaction.atomic`. If any exception occurs (e.g., password too short), it rolls back the entire database state.
3.  **Default Setup**: Automatically creates an "Admin" role and gives it default permissions like `add_user` and `view_audit_logs`.

#### 📂 Key Files:
- `tenants/services.py`: The orchestration logic.

---

## 4. Team Invite System (Secure Scaling)

### 🔴 The Problem
Inviting users via email requires a secure way to verify them without revealing their tenant membership to the public until they are authenticated.

### 🟢 The Solution: Tokenized Invitations
A state-managed invitation system using UUID tokens.

#### 🛠️ Logic Flow:
1.  **Send**: `InvitationService.create_invitation` generates a UUID token and sets an expiry date.
2.  **View**: The user visits `/invite/accept/<token>/`. The view is **Unscoped**, meaning it can "see" the invitation even if it doesn't know the tenant yet.
3.  **Accept**: Upon login/confirmation, the system creates a `Membership` and marks the invitation `is_accepted=True`.
4.  **Management**: Admins can `Resend` (extend expiry) or `Revoke` (delete) invites from their dashboard.

#### 📂 Key Files:
- `tenants/models.py`: `TenantInvitation` model.
- `tenants/services_invitation.py`: Invitation logic.
- `tenants/views_dashboard.py`: Invite management views.

---

## 5. Cloud-Agnostic Storage (Strategy Pattern)

### 🔴 The Problem
You don't want to hardcode your file paths to a local folder, and you definitely don't want a "tenant leak" where one user can guess the URL of another user's private files.

### 🟢 The Solution: Dynamic Silos
We use a strategy function for pathing and an adapter for storage.

#### 🛠️ Implementation Details:
1.  **Dyanmic Pathing**: `tenants/utils_storage.py` provides `tenant_file_path`. It uses the **Tenant ID** as a root folder.
2.  **Naming Security**: Filenames are automatically hashed to UUIDs to prevent directory traversal or file-id guessing.
3.  **Abstraction**: By using `django-storages`, the `Product.image` field works the same way if you use Local Disk, AWS S3, or Google Cloud. You only change the `DEFAULT_FILE_STORAGE` setting.

#### 📂 Key Files:
- `tenants/utils_storage.py`: Path generation logic.

---

## 6. End-to-End Audit Logging (Observer Pattern)

### 🔴 The Problem
In enterprise software, you must be able to answer: "Who changed the price of this product at 3 AM?"

### 🟢 The Solution: Global Change Tracking
A silent background engine that tracks every database mutation.

#### 🛠️ Implementation Details:
1.  **Global Context Middleware**: Captures the `User` from the request and stores it in thread-local context (`tenants/middleware_user.py`).
2.  **Signals**: `tenants/signals.py` listens for `pre_save` (to get old values) and `post_save` (to record new values).
3.  **JSON Diffing**: The `AuditService` calculates which fields changed and stores them in a `JSONField`.
4.  **Automated**: Works for *any* model inheriting from `TenantAwareModel` without additional code.

#### 📂 Key Files:
- `tenants/services_audit.py`: The diffing logic.
- `tenants/signals.py`: The triggers.
- `tenants/middleware_user.py`: The user context "bridge".

---

## 7. Enterprise Custom Domains (Dynamic Routing)

### 🔴 The Problem
Enterprise clients often refuse to use your subdomain (e.g., `acme.myaas.com`) and insist on their own domain (e.g., `portal.acme.com`).

### 🟢 The Solution: Domain-Agnostic Routing
A smart router that resolves any host to a tenant.

#### 🛠️ Implementation Details:
1.  **Domain Registry**: The `Domain` model tracks `is_custom` and `status`.
2.  **DNS Verification**: `DomainService` uses `dnspython` to perform actual CNAME lookups against the live internet.
3.  **Middleware Fallback**: The `TenantMiddleware` now looks up the *entire* host string in the `Domain` table. If it finds a match, it activates that tenant—whether it's a subdomain or a full external domain.

#### 📂 Key Files:
- `tenants/services_domain.py`: DNS verification engines.
- `tenants/middleware.py`: The routing logic.

---

## 8. Global Search (cross-resource)

### 🔴 The Problem
Users need to quickly find information across different parts of their application (e.g., products, users, audit logs) without navigating to separate sections. Traditional search often requires separate implementations for each model, leading to inconsistent results and complex maintenance.

### 🟢 The Solution: Unified Query Layer with Tenant-Scoped Aggregation
We provide a single, intelligent search endpoint that aggregates results from multiple database models concurrently, all while respecting tenant isolation.

#### 🛠️ Implementation Details:
1.  **Search Service**: A dedicated `SearchService` orchestrates the search process. It takes a query string and a list of models to search.
2.  **Tenant-Locked Queries**: For each specified model, the `SearchService` executes a separate, tenant-scoped query. Because the ORM is already configured for multi-tenancy (via `TenantManager`), every search automatically filters data to the current tenant, ensuring zero data leakage across workspaces.
3.  **Dynamic Aggregation**: Results from different models are collected, normalized, and then grouped by category (e.g., "Products", "Members", "Audit Logs").
4.  **HTMX Powered Frontend**: The search interface uses HTMX to provide real-time "Type-to-Search" results. As the user types, results are fetched and displayed instantly, often with visual hit categorization and hit counts for each resource type.

#### 🛡️ Security Check:
When a user searches for "iPhone", the system performs a multi-resource scan. Since searching happens inside the Tenant Context, the user only finds "iPhones" belonging to their organization, even if other tenants have products with similar names.

#### 📂 Key Files:
- `tenants/services_search.py`: The core search orchestration and aggregation logic.
- `tenants/views_dashboard.py`: The view handling search requests and rendering HTMX responses.
- `tenants/models.py`: Models that are searchable will have appropriate fields indexed or configured for full-text search.
