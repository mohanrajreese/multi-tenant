from tenants.infrastructure.adapters.database.factory import DatabaseFactory
from tenants.infrastructure.adapters.communication.factory import CommunicationFactory
from tenants.infrastructure.adapters.storage.factory import StorageFactory
from tenants.infrastructure.adapters.identity.factory import IdentityFactory
from tenants.infrastructure.adapters.intelligence.factory import LLMFactory
from tenants.infrastructure.adapters.audit.factory import AuditFactory
from tenants.infrastructure.adapters.search.factory import SearchFactory
from tenants.infrastructure.adapters.performance.factory import CacheFactory, QueueFactory
from tenants.infrastructure.adapters.control.factory import ControlFactory
from tenants.infrastructure.utils.resilience import circuit_breaker
from tenants.infrastructure.utils.telemetry import get_tracer

tracer = get_tracer()

class InfrastructureHub:
    """
    Tier 60: The Infrastructure Singularity.
    Centralized access point for all sovereign infrastructure providers.
    """
    
    @staticmethod
    def database():
        """Returns the active Database Provider (Global/Tenant-Aware)."""
        return DatabaseFactory.get_provider()

    @staticmethod
    @circuit_breaker(threshold=5, reset_timeout=60)
    def email(tenant):
        """Returns the tenant's Email Provider."""
        with tracer.start_as_current_span("hub.email", attributes={"tenant.slug": tenant.slug}):
            return CommunicationFactory.get_email_provider(tenant)

    @staticmethod
    @circuit_breaker(threshold=5, reset_timeout=60)
    def sms(tenant):
        """Returns the tenant's SMS Provider."""
        with tracer.start_as_current_span("hub.sms", attributes={"tenant.slug": tenant.slug}):
            return CommunicationFactory.get_sms_provider(tenant)

    @staticmethod
    @circuit_breaker(threshold=5, reset_timeout=60)
    def storage(tenant):
        """Returns the tenant's Storage Provider."""
        with tracer.start_as_current_span("hub.storage", attributes={"tenant.slug": tenant.slug}):
            return StorageFactory.get_provider(tenant)

    @staticmethod
    @circuit_breaker(threshold=5, reset_timeout=60)
    def identity(tenant, provider_type='google'):
        """Returns the tenant's Identity Provider."""
        with tracer.start_as_current_span("hub.identity", attributes={"tenant.slug": tenant.slug, "provider": provider_type}):
            return IdentityFactory.get_provider(tenant, provider_type)

    @staticmethod
    @circuit_breaker(threshold=5, reset_timeout=60)
    def intelligence(tenant):
        """Returns the tenant's Intelligence (AI) Provider."""
        with tracer.start_as_current_span("hub.intelligence", attributes={"tenant.slug": tenant.slug}):
            return LLMFactory.get_provider(tenant)

    @staticmethod
    @circuit_breaker(threshold=5, reset_timeout=60)
    def audit(tenant):
        """Returns the tenant's Audit/Compliance Provider."""
        with tracer.start_as_current_span("hub.audit", attributes={"tenant.slug": tenant.slug}):
            return AuditFactory.get_provider(tenant)

    @staticmethod
    @circuit_breaker(threshold=5, reset_timeout=60)
    def search(tenant):
        """Returns the tenant's Search Provider."""
        with tracer.start_as_current_span("hub.search", attributes={"tenant.slug": tenant.slug}):
            return SearchFactory.get_provider(tenant)

    @staticmethod
    @circuit_breaker(threshold=5, reset_timeout=60)
    def cache(tenant):
        """Returns the tenant's Cache Provider."""
        with tracer.start_as_current_span("hub.cache", attributes={"tenant.slug": tenant.slug}):
            return CacheFactory.get_provider(tenant)

    @staticmethod
    @circuit_breaker(threshold=5, reset_timeout=60)
    def queue(tenant):
        """Returns the tenant's Queue/Task Provider."""
        with tracer.start_as_current_span("hub.queue", attributes={"tenant.slug": tenant.slug}):
            return QueueFactory.get_provider(tenant)

    @staticmethod
    @circuit_breaker(threshold=5, reset_timeout=60)
    def control(tenant):
        """Returns the tenant's Feature Flag/Control Provider."""
        with tracer.start_as_current_span("hub.control", attributes={"tenant.slug": tenant.slug}):
            return ControlFactory.get_provider(tenant)

    @staticmethod
    @circuit_breaker(threshold=5, reset_timeout=60)
    def whatsapp(tenant):
        """Returns the tenant's WhatsApp Provider."""
        with tracer.start_as_current_span("hub.whatsapp", attributes={"tenant.slug": tenant.slug}):
            return CommunicationFactory.get_whatsapp_provider(tenant)
