from django.conf import settings
from tenants.infrastructure.protocols_database import IDatabaseProvider
from tenants.infrastructure.database.impl import SchemaManager

class PostgresSchemaProvider(IDatabaseProvider):
    """
    Tier 56: PostgreSQL Schema Isolation Provider.
    Implements database sovereignty via schema separation.
    """
    
    def create_tenant_store(self, tenant_slug: str) -> bool:
        if SchemaManager.schema_exists(tenant_slug):
            return False
        SchemaManager.create_schema(tenant_slug)
        return True

    def delete_tenant_store(self, tenant_slug: str) -> bool:
        if not SchemaManager.schema_exists(tenant_slug):
            return False
        # Drop schema cascade
        with connection.cursor() as cursor:
            cursor.execute(f"DROP SCHEMA IF EXISTS \"{tenant_slug}\" CASCADE")
        return True
        
    def activate_context(self, tenant_slug: str) -> None:
        SchemaManager.activate_schema(tenant_slug)
        
    def deactivate_context(self) -> None:
        SchemaManager.deactivate_schema()
        
    def run_migrations(self, tenant_slug: str) -> list:
        from django.core.management import call_command
        # This is a simplified version; in production we use the migrate_schemas command logic
        # For the provider interface, we ideally want to invoke the migration executor directly
        # or call the management command scoped to this schema.
        # Returning empty list as migration output capture is complex here
        return []

class SqliteProvider(IDatabaseProvider):
    """
    Tier 56: SQLite Provider (No-Op for Schema Isolation).
    SQLite does not support schemas in the same way. 
    This is primarily for dev/test environments where isolation is logical only.
    """
    def create_tenant_store(self, tenant_slug: str) -> bool:
        return True # specific logic if using separate db files

    def delete_tenant_store(self, tenant_slug: str) -> bool:
        return True
        
    def activate_context(self, tenant_slug: str) -> None:
        pass # No schema switching in standard sqlite
        
    def deactivate_context(self) -> None:
        pass
        
    def run_migrations(self, tenant_slug: str) -> list:
        return []
