from .providers.smtp import SMTPProvider
from .providers.sendgrid import SendGridProvider
from .providers.ses import SESProvider
from .providers.twilio import TwilioProvider
from .providers.whatsapp import TwilioWhatsAppProvider
from tenants.infrastructure.security.vault import SovereignVault

class CommunicationFactory:
    """
    Factory to resolve communication providers based on tenant configuration.
    """
    
    @staticmethod
    def get_email_provider(tenant):
        """
        Returns the configured Email provider for the tenant.
        """
        config = tenant.config.get('communication', {}).get('email', {})
        # Tier 91: Unprotect sensitive credentials
        config = SovereignVault.unprotect_config(config, ['api_key', 'password', 'secret_key'])
        
        provider_type = config.get('provider', 'smtp') # Default to SMTP
        
        if provider_type == 'smtp':
            return SMTPProvider(config)
        elif provider_type == 'sendgrid':
            return SendGridProvider(config)
        elif provider_type == 'ses':
            return SESProvider(config)
        
        # Fallback/Default
        return SMTPProvider(config)

    @staticmethod
    def get_sms_provider(tenant):
        """
        Returns the configured SMS provider for the tenant.
        """
        config = tenant.config.get('communication', {}).get('sms', {})
        # Tier 91: Unprotect sensitive credentials
        config = SovereignVault.unprotect_config(config, ['api_key', 'auth_token', 'account_sid'])
        
        provider_type = config.get('provider', 'twilio') # Default to Twilio
        
        if provider_type == 'twilio':
            return TwilioProvider(config)
        
        return TwilioProvider(config)

    @staticmethod
    def get_whatsapp_provider(tenant):
        """
        Returns the configured WhatsApp provider for the tenant.
        """
        config = tenant.config.get('communication', {}).get('whatsapp', {})
        # Tier 91: Unprotect sensitive credentials
        config = SovereignVault.unprotect_config(config, ['api_key', 'auth_token', 'account_sid'])
        
        provider_type = config.get('provider', 'twilio') # Default to Twilio
        
        if provider_type == 'twilio':
            return TwilioWhatsAppProvider(config)
        
        return TwilioWhatsAppProvider(config)
