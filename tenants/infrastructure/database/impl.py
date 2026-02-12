from django.db import connection

class SQLiteSchemaSimulator:
    """Mock for SQLite to prevent crashes while demonstrating Apex logic."""
    @staticmethod
    def set_schema(schema_name):
        pass # SQLite doesn't have search_path

    @staticmethod
    def create_schema(schema_name):
        pass

class PostgresSchemaManager:
    """Apex Tier: Real Physical Isolation using PostgreSQL Schemas."""
    
    @staticmethod
    def set_schema(schema_name):
        """Switches the current database connection to the specified schema."""
        with connection.cursor() as cursor:
            # We also include 'public' for shared tables (Plans, etc.)
            cursor.execute(f"SET search_path TO {schema_name}, public")

    @staticmethod
    def create_schema(schema_name):
        """Creates a new physical schema for a tenant."""
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")

class SchemaManager:
    """The Apex Resolver: Automatically selects the correct manager."""
    
    @staticmethod
    def get_manager():
        if connection.vendor == 'postgresql':
            return PostgresSchemaManager()
        return SQLiteSchemaSimulator()

    @classmethod
    def set_active_schema(cls, schema_name):
        cls.get_manager().set_schema(schema_name)

    @classmethod
    def provision_schema(cls, schema_name):
        cls.get_manager().create_schema(schema_name)

    # Alias for compatibility with the new provider logic if needed,
    # or the provider can use this class directly.
    activate_schema = set_active_schema
    deactivate_schema = lambda: PostgresSchemaManager.set_schema('public')
    @staticmethod
    def schema_exists(schema_name):
        if connection.vendor != 'postgresql':
            return False
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM information_schema.schemata WHERE schema_name = %s",
                [schema_name]
            )
            return cursor.fetchone() is not None
