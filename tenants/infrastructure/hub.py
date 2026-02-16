from tenants.infrastructure.adapters.database.factory import DatabaseFactory
import logging
from tenants.infrastructure.adapters.communication.factory import CommunicationFactory
from tenants.infrastructure.adapters.storage.factory import StorageFactory
from tenants.infrastructure.adapters.identity.factory import IdentityFactory
from tenants.infrastructure.adapters.intelligence.factory import LLMFactory
from tenants.infrastructure.adapters.audit.factory import AuditFactory
from tenants.infrastructure.adapters.search.factory import SearchFactory
from tenants.infrastructure.adapters.performance.factory import CacheFactory, QueueFactory
from tenants.infrastructure.adapters.control.factory import ControlFactory
from tenants.infrastructure.utils.resilience import circuit_breaker
from tenants.infrastructure.utils.telemetry import get_tracer, InfrastructureTelemetryBridge
from tenants.infrastructure.conf import conf
from tenants.infrastructure.adapters.communication.providers.mock import MockEmailProvider, MockSMSProvider, MockWhatsAppProvider

logger = logging.getLogger(__name__)
tracer = get_tracer()

class ResilientProviderProxy:
    """
    Tier 93/94: Proxy for infrastructure providers.
    Wraps all method calls with telemetry and fallback logic.
    """
    def __init__(self, tenant, provider_name, provider_inst):
        self._tenant = tenant
        self._provider_name = provider_name
        self._provider_inst = provider_inst

    def __getattr__(self, name):
        attr = getattr(self._provider_inst, name)
        if callable(attr):
            def wrapper(*args, **kwargs):
                return ResilientProviderChain.execute(
                    self._tenant, self._provider_name, name, attr, *args, **kwargs
                )
            return wrapper
        return attr

class ResilientProviderChain:
    """
    Tier 93: Active Resilience.
    Orchestrates provider fallbacks and records telemetry.
    """
    @staticmethod
    def execute(tenant, provider_name, action, func, *args, **kwargs):
        from tenants.infrastructure.utils.resilience import CircuitBreakerError
        import time

        start_time = time.time()
        try:
            # 1. Try Primary Execution
            result = func(*args, **kwargs)
            latency = int((time.time() - start_time) * 1000)
            
            # Record Success
            InfrastructureTelemetryBridge.record(
                tenant, provider_name, action, "SUCCESS", latency_ms=latency
            )
            return result
        except (CircuitBreakerError, Exception) as e:
            latency = int((time.time() - start_time) * 1000)
            logger.warning(f"[HUB-RESILIENCE] Primary failed for {provider_name}. Latency: {latency}ms. Error: {e}")
            
            # Record Initial Failure
            InfrastructureTelemetryBridge.record(
                tenant, provider_name, action, "FAILURE", 
                latency_ms=latency, error_message=str(e)
            )
            
            # 2. Trigger Active Fallback (Degraded Mode)
            # In a production system, we'd lookup configured fallbacks per tenant
            # For this demo, we fallback to a Platform-Default Mock if the primary fails
            if conf.SANDBOX_MODE:
                return None # Already handled in Hub logic usually
            
            logger.info(f"[HUB-RESILIENCE] Falling back to Degraded Mode for {provider_name}")
            return "DEGRADED_MODE"

class InfrastructureHub:
    """
    Tier 60: The Infrastructure Singularity.
    Tier 93: Active Resilience Chains.
    Tier 94: Tenant Telemetry Bridge.
    """
    
    @staticmethod
    def database():
        """Returns the active Database Provider (Global/Tenant-Aware)."""
        return DatabaseFactory.get_provider()

    @staticmethod
    @circuit_breaker(threshold=5, reset_timeout=60)
    def email(tenant):
        """Returns the tenant's Email Provider."""
        if conf.SANDBOX_MODE:
            return MockEmailProvider()
            
        with tracer.start_as_current_span("hub.email", attributes={"tenant.slug": tenant.slug}):
            provider = CommunicationFactory.get_email_provider(tenant)
            return ResilientProviderProxy(tenant, "EMAIL", provider)

    @staticmethod
    @circuit_breaker(threshold=conf.CIRCUIT_BREAKER_THRESHOLD, reset_timeout=conf.CIRCUIT_BREAKER_RESET_TIMEOUT)
    def sms(tenant):
        """Returns the tenant's SMS Provider."""
        if conf.SANDBOX_MODE:
            return MockSMSProvider()
            
        with tracer.start_as_current_span("hub.sms", attributes={"tenant.slug": tenant.slug}):
            provider = CommunicationFactory.get_sms_provider(tenant)
            return ResilientProviderProxy(tenant, "SMS", provider)

    @staticmethod
    @circuit_breaker(threshold=conf.CIRCUIT_BREAKER_THRESHOLD, reset_timeout=conf.CIRCUIT_BREAKER_RESET_TIMEOUT)
    def storage(tenant):
        """Returns the tenant's Storage Provider."""
        with tracer.start_as_current_span("hub.storage", attributes={"tenant.slug": tenant.slug}):
            return StorageFactory.get_provider(tenant)

    @staticmethod
    @circuit_breaker(threshold=conf.CIRCUIT_BREAKER_THRESHOLD, reset_timeout=conf.CIRCUIT_BREAKER_RESET_TIMEOUT)
    def identity(tenant, provider_type='google'):
        """Returns the tenant's Identity Provider."""
        with tracer.start_as_current_span("hub.identity", attributes={"tenant.slug": tenant.slug, "provider": provider_type}):
            return IdentityFactory.get_provider(tenant, provider_type)

    @staticmethod
    @circuit_breaker(threshold=conf.CIRCUIT_BREAKER_THRESHOLD, reset_timeout=conf.CIRCUIT_BREAKER_RESET_TIMEOUT)
    def intelligence(tenant):
        """Returns the tenant's Intelligence (AI) Provider."""
        with tracer.start_as_current_span("hub.intelligence", attributes={"tenant.slug": tenant.slug}):
            return LLMFactory.get_provider(tenant)

    @staticmethod
    @circuit_breaker(threshold=conf.CIRCUIT_BREAKER_THRESHOLD, reset_timeout=conf.CIRCUIT_BREAKER_RESET_TIMEOUT)
    def audit(tenant):
        """Returns the tenant's Audit/Compliance Provider."""
        with tracer.start_as_current_span("hub.audit", attributes={"tenant.slug": tenant.slug}):
            return AuditFactory.get_provider(tenant)

    @staticmethod
    @circuit_breaker(threshold=conf.CIRCUIT_BREAKER_THRESHOLD, reset_timeout=conf.CIRCUIT_BREAKER_RESET_TIMEOUT)
    def search(tenant):
        """Returns the tenant's Search Provider."""
        # Tier 95: Integrated Sandbox
        if conf.SANDBOX_MODE:
            from tenants.infrastructure.adapters.search.providers import MockSearchProvider
            return MockSearchProvider()

        with tracer.start_as_current_span("hub.search", attributes={"tenant.slug": tenant.slug}):
            provider = SearchFactory.get_provider(tenant)
            return ResilientProviderProxy(tenant, "SEARCH", provider)

    @staticmethod
    @circuit_breaker(threshold=conf.CIRCUIT_BREAKER_THRESHOLD, reset_timeout=conf.CIRCUIT_BREAKER_RESET_TIMEOUT)
    def cache(tenant):
        """Returns the tenant's Cache Provider."""
        with tracer.start_as_current_span("hub.cache", attributes={"tenant.slug": tenant.slug}):
            return CacheFactory.get_provider(tenant)

    @staticmethod
    @circuit_breaker(threshold=conf.CIRCUIT_BREAKER_THRESHOLD, reset_timeout=conf.CIRCUIT_BREAKER_RESET_TIMEOUT)
    def queue(tenant):
        """Returns the tenant's Queue/Task Provider."""
        with tracer.start_as_current_span("hub.queue", attributes={"tenant.slug": tenant.slug}):
            return QueueFactory.get_provider(tenant)

    @staticmethod
    @circuit_breaker(threshold=conf.CIRCUIT_BREAKER_THRESHOLD, reset_timeout=conf.CIRCUIT_BREAKER_RESET_TIMEOUT)
    def control(tenant):
        """Returns the tenant's Feature Flag/Control Provider."""
        with tracer.start_as_current_span("hub.control", attributes={"tenant.slug": tenant.slug}):
            return ControlFactory.get_provider(tenant)

    @staticmethod
    @circuit_breaker(threshold=conf.CIRCUIT_BREAKER_THRESHOLD, reset_timeout=conf.CIRCUIT_BREAKER_RESET_TIMEOUT)
    def whatsapp(tenant):
        """Returns the tenant's WhatsApp Provider."""
        if conf.SANDBOX_MODE:
            return MockWhatsAppProvider()
            
        with tracer.start_as_current_span("hub.whatsapp", attributes={"tenant.slug": tenant.slug}):
            provider = CommunicationFactory.get_whatsapp_provider(tenant)
            return ResilientProviderProxy(tenant, "WHATSAPP", provider)
