from tenants.infrastructure.adapters.database.factory import DatabaseFactory

class SovereignSchemaManager:
    """The Apex Resolver: Delegates to the active DatabaseProvider."""
    
    @staticmethod
    def set_active_schema(schema_name):
        DatabaseFactory.get_provider().activate_context(schema_name)

    @staticmethod
    def provision_schema(schema_name):
        return DatabaseFactory.get_provider().create_tenant_store(schema_name)

    @staticmethod
    def deprovision_schema(schema_name):
        return DatabaseFactory.get_provider().delete_tenant_store(schema_name)
