from django.core.cache import cache
from .utils import get_current_tenant

class TenantCache:
    """
    Zenith Tier: Performance & Isolation utility.
    Automatically prefixes every cache key with the current tenant_id.
    """

    @staticmethod
    def _make_key(key):
        tenant = get_current_tenant()
        tenant_prefix = str(tenant.id) if tenant else "public"
        return f"tenant:{tenant_prefix}:{key}"

    @classmethod
    def set(cls, key, value, timeout=None):
        return cache.set(cls._make_key(key), value, timeout)

    @classmethod
    def get(cls, key, default=None):
        return cache.get(cls._make_key(key), default)

    @classmethod
    def delete(cls, key):
        return cache.delete(cls._make_key(key))

    @classmethod
    def get_or_set(cls, key, default_func, timeout=None):
        """
        Standard get_or_set but tenant-aware.
        """
        full_key = cls._make_key(key)
        val = cache.get(full_key)
        if val is None:
            val = default_func()
            cache.set(full_key, val, timeout)
        return val
