import time
import logging
from django.core.cache import cache
from django.http import JsonResponse
from tenants.infrastructure.utils import get_current_tenant

logger = logging.getLogger(__name__)

class ResourceGovernorMiddleware:
    """
    Psi Tier: Operational Resilience - Resource Governor.
    Detects and isolates 'Noisy Neighbors' (tenants causing performance degradation).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tenant = get_current_tenant()
        if not tenant:
            return self.get_response(request)

        # 1. Check if tenant is manually Quarantined
        if tenant.config.get('resilience', {}).get('quarantined', False):
            logger.warning(f"Blocking request for Quarantined Tenant: {tenant.slug}")
            return JsonResponse({
                "error": "This organization is temporarily isolated for resource protection.",
                "code": "TENANT_QUARANTINED"
            }, status=403)

        # 2. Automated Rate Limiting / Slow Down (Noisy Neighbor Protection)
        # We track request velocity in the last 1 minute in cache
        cache_key = f"governor_velocity_{tenant.id}"
        velocity = cache.get(cache_key, 0)
        
        # Soft Limit: Slow down
        if velocity > 1000: # 1k requests/min
            time.sleep(0.1) # Artificially inject latency to protect shared resources
            logger.info(f"Injecting protective latency for high-velocity tenant: {tenant.slug}")

        # Hard Limit: Quarantine
        if velocity > 5000: # 5k requests/min
            cache.set(f"auto_quarantine_{tenant.id}", True, timeout=300)
            logger.error(f"AUTO-QUARANTINE triggered for {tenant.slug} due to velocity spike ({velocity})")

        # Increment velocity
        cache.set(cache_key, velocity + 1, timeout=60)

        response = self.get_response(request)
        
        # 3. Error Rate Isolation
        if response.status_code >= 500:
            err_key = f"governor_errors_{tenant.id}"
            err_count = cache.get(err_key, 0) + 1
            cache.set(err_key, err_count, timeout=60)
            
            if err_count > 50: # More than 50 server errors per minute
                logger.critical(f"HEALTH WARNING: Tenant {tenant.slug} is experiencing high error rates ({err_count}/min).")

        return response
