from tenants.infrastructure.adapters.database.factory import DatabaseFactory
from tenants.infrastructure.adapters.communication.factory import CommunicationFactory
from tenants.infrastructure.adapters.storage.factory import StorageFactory
from tenants.infrastructure.adapters.identity.factory import IdentityFactory
from tenants.infrastructure.adapters.intelligence.factory import LLMFactory
from tenants.infrastructure.adapters.audit.factory import AuditFactory
from tenants.infrastructure.adapters.search.factory import SearchFactory
from tenants.infrastructure.adapters.performance.factory import CacheFactory, QueueFactory
from tenants.infrastructure.adapters.control.factory import ControlFactory

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
    def email(tenant):
        """Returns the tenant's Email Provider."""
        return CommunicationFactory.get_email_provider(tenant)

    @staticmethod
    def sms(tenant):
        """Returns the tenant's SMS Provider."""
        return CommunicationFactory.get_sms_provider(tenant)

    @staticmethod
    def storage(tenant):
        """Returns the tenant's Storage Provider."""
        return StorageFactory.get_provider(tenant)

    @staticmethod
    def identity(tenant, provider_type='google'):
        """Returns the tenant's Identity Provider."""
        return IdentityFactory.get_provider(tenant, provider_type)

    @staticmethod
    def intelligence(tenant):
        """Returns the tenant's Intelligence (AI) Provider."""
        return LLMFactory.get_provider(tenant)

    @staticmethod
    def audit(tenant):
        """Returns the tenant's Audit/Compliance Provider."""
        return AuditFactory.get_provider(tenant)

    @staticmethod
    def search(tenant):
        """Returns the tenant's Search Provider."""
        return SearchFactory.get_provider(tenant)

    @staticmethod
    def cache(tenant):
        """Returns the tenant's Cache Provider."""
        return CacheFactory.get_provider(tenant)

    @staticmethod
    def queue(tenant):
        """Returns the tenant's Queue/Task Provider."""
        return QueueFactory.get_provider(tenant)

    @staticmethod
    def control(tenant):
        """Returns the tenant's Feature Flag/Control Provider."""
        return ControlFactory.get_provider(tenant)
