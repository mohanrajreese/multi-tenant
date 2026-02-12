from django.conf import settings
from tenants.infrastructure.conf import conf
from .providers import PostgresSchemaProvider, SqliteProvider

class DatabaseFactory:
    """
    Factory to resolve the active database provider.
    """
    _instance = None

    @classmethod
    def get_provider(cls):
        if cls._instance:
            return cls._instance
            
        db_engine = settings.DATABASES['default']['ENGINE']
        
        if 'postgresql' in db_engine:
            cls._instance = PostgresSchemaProvider()
        else:
            cls._instance = SqliteProvider()
            
        return cls._instance
