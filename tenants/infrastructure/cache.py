from django.core.cache import cache
from tenants.infrastructure.utils.context import get_current_tenant

class TenantCache:
    """
    Sovereign Cache Wrapper.
    """
    
    @staticmethod
    def _get_key(key):
        tenant = get_current_tenant()
        prefix = str(tenant.id) if tenant else "shared"
        return f"tenant:{prefix}:{key}"

    @staticmethod
    def _get_provider():
        from tenants.infrastructure.utils.context import get_current_tenant
        from tenants.infrastructure.adapters.performance.factory import CacheFactory
        
        tenant = get_current_tenant()
        if not tenant:
            # Fallback to default cache for system ops
            from django.core.cache import cache
            return cache
            
        return CacheFactory.get_provider(tenant)

    @classmethod
    def get(cls, key, default=None):
        return cls._get_provider().get(cls._get_key(key), default)

    @classmethod
    def set(cls, key, value, timeout=300):
        return cls._get_provider().set(cls._get_key(key), value, timeout)

    @classmethod
    def delete(cls, key):
        return cls._get_provider().delete(cls._get_key(key))

    @classmethod
    def get_or_set(cls, key, default_func, timeout=3600):
        """Standard Django get_or_set but with tenant prefixing."""
        full_key = cls._get_key(key)
        val = cls._get_provider().get(full_key)
        if val is None:
            val = default_func()
            cache.set(full_key, val, timeout)
        return val
