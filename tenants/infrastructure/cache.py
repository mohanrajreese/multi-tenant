from django.core.cache import cache
from tenants.infrastructure.utils.context import get_current_tenant

class TenantCache:
    """
    Final Frontier Improvisation: Tenant-Aware Cache Wrapper.
    Automatically prefixes every key with the current tenant ID to 
    prevent 'Cache Poisoning' in multi-tenant environments.
    """
    
    @staticmethod
    def _get_key(key):
        tenant = get_current_tenant()
        prefix = str(tenant.id) if tenant else "shared"
        return f"tenant:{prefix}:{key}"

    @classmethod
    def get(cls, key, default=None):
        return cache.get(cls._get_key(key), default)

    @classmethod
    def set(cls, key, value, timeout=3600):
        cache.set(cls._get_key(key), value, timeout)

    @classmethod
    def delete(cls, key):
        cache.delete(cls._get_key(key))

    @classmethod
    def get_or_set(cls, key, default_func, timeout=3600):
        """Standard Django get_or_set but with tenant prefixing."""
        full_key = cls._get_key(key)
        val = cache.get(full_key)
        if val is None:
            val = default_func()
            cache.set(full_key, val, timeout)
        return val
