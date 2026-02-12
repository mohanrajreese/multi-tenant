from rest_framework.throttling import SimpleRateThrottle

class TenantRateThrottle(SimpleRateThrottle):
    """
    Limits the rate of API requests per tenant (Organization).
    This prevents one tenant from degrading performance for others.
    """
    scope = 'tenant'

    def get_cache_key(self, request, view):
        tenant = getattr(request, 'tenant', None)
        if not tenant:
            return None  # Fallback to default or skip

        return self.cache_format % {
            'scope': self.scope,
            'ident': str(tenant.id)
        }
