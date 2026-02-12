from rest_framework.throttling import SimpleRateThrottle

class TenantRateThrottle(SimpleRateThrottle):
    """
    Limits the rate of API requests per tenant (Organization).
    This prevents one tenant from degrading performance for others.
    """
    scope = 'tenant'

    rate = '1000/hour'

    def get_cache_key(self, request, view):
        from tenants.infrastructure.utils.context import get_current_tenant
        tenant = get_current_tenant()
        
        if not tenant:
            return None 

        # Dynamic Rate Limit from Tenant Config
        config_rate = tenant.config.get('control', {}).get('rate_limit')
        if config_rate:
            self.rate = config_rate
            self.num_requests, self.duration = self.parse_rate(self.rate)

        return self.cache_format % {
            'scope': self.scope,
            'ident': str(tenant.id)
        }
