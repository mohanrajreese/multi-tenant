from typing import Protocol, runtime_checkable, Any, List

@runtime_checkable
class IDatabaseProvider(Protocol):
    """
    Tier 56: Database Sovereignty Protocol.
    Abstracts the underlying mechanism of tenant data isolation.
    """
    def create_tenant_store(self, tenant_slug: str) -> bool:
        """Initialize the storage area (e.g., Schema) for a new tenant."""
        ...

    def delete_tenant_store(self, tenant_slug: str) -> bool:
        """Destroy the storage area for a tenant."""
        ...
        
    def activate_context(self, tenant_slug: str) -> None:
        """Switch the current execution context to the tenant's store."""
        ...
        
    def deactivate_context(self) -> None:
        """Revert execution context to the public/shared store."""
        ...
        
    def run_migrations(self, tenant_slug: str) -> List[str]:
        """Apply pending migrations to the tenant's store."""
        ...
