from tenants.infrastructure.adapters.database.factory import DatabaseFactory
from tenants.infrastructure.adapters.communication.factory import CommunicationFactory
from tenants.infrastructure.adapters.storage.factory import StorageFactory
from tenants.infrastructure.adapters.identity.factory import IdentityFactory
from tenants.infrastructure.adapters.intelligence.factory import LLMFactory
from tenants.infrastructure.adapters.audit.factory import AuditFactory

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
