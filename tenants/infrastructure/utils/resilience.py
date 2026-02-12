import functools
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)

class CircuitBreakerError(Exception):
    """Exception raised when a circuit is open."""
    def __init__(self, message, retry_after=60):
        self.message = message
        self.retry_after = retry_after
        super().__init__(self.message)

def circuit_breaker(threshold=5, reset_timeout=60):
    """
    Tier 70: Regional Circuit Breaker.
    Prevents cascading failures by tripping after 'threshold' consecutive failures.
    Stored in Django cache for distributed state coordination.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 1. Resolve Tenant Context
            from tenants.domain.models import Tenant
            tenant = kwargs.get('tenant')
            if not tenant:
                for arg in args:
                    if isinstance(arg, Tenant):
                        tenant = arg
                        break
            
            tenant_slug = tenant.slug if tenant else "global"
            # Use a stabilized name for the provider
            provider_name = func.__name__
            
            cache_key_failures = f"cb_fail_{tenant_slug}_{provider_name}"
            cache_key_state = f"cb_state_{tenant_slug}_{provider_name}"
            
            # 2. Check if circuit is OPEN
            if cache.get(cache_key_state) == "OPEN":
                logger.warning(f"Circuit {provider_name} is OPEN for tenant {tenant_slug}")
                raise CircuitBreakerError(
                    f"Infrastructure component '{provider_name}' is currently unavailable for {tenant_slug}.",
                    retry_after=reset_timeout
                )
            
            try:
                result = func(*args, **kwargs)
                # Success: reset failure counter upon successful execution
                if cache.get(cache_key_failures):
                    cache.delete(cache_key_failures)
                return result
            except Exception as e:
                # Don't trip for validation errors or expected business exceptions
                # We only want to trip for infrastructure outages (Timeout, Connection Refused, etc)
                # For now, we trip for any non-SovereignError or non-validation error if we can detect them
                # But let's keep it simple: trip for any unhandled exception.
                
                failures = cache.get(cache_key_failures, 0) + 1
                cache.set(cache_key_failures, failures, timeout=reset_timeout * 2)
                
                logger.error(f"[CIRCUIT] Failure in {provider_name} for {tenant_slug} ({failures}/{threshold}): {str(e)}")
                
                if failures >= threshold:
                    logger.critical(f"[CIRCUIT] Tripping circuit '{provider_name}' for tenant {tenant_slug} for {reset_timeout}s!")
                    cache.set(cache_key_state, "OPEN", timeout=reset_timeout)
                
                raise e
        return wrapper
    return decorator
