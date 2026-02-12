from django.conf import settings
from .communication.factory import CommunicationFactory

class TenantEmailService:
    """
    Sovereign Tier: Provider-Agnostic Communication.
    Uses CommunicationFactory to dynamically route alerts through each tenant's 
    preferred provider (SMTP, SendGrid, etc.).
    """

    @staticmethod
    def send_tenant_email(tenant, subject, message, recipient_list, **kwargs):
        """
        Sends an email with tenant-specific branding and provider.
        """
        brand_name = tenant.name
        support_email = tenant.support_email or getattr(settings, 'DEFAULT_FROM_EMAIL', 'support@platform.com')
        
        # Add a branded footer to the message
        footer = f"\n\n---\nSent by {brand_name}\n"
        if tenant.website:
            footer += f"Visit us: {tenant.website}"
            
        full_message = message + footer
        
        # Resolve the agnostic provider
        provider = CommunicationFactory.get_email_provider(tenant)
        
        # Send to all recipients
        results = []
        for recipient in recipient_list:
            results.append(
                provider.send_email(
                    recipient=recipient,
                    subject=subject,
                    body=full_message,
                    from_email=f"{brand_name} <{support_email}>",
                    **kwargs
                )
            )
        return all(results)

    @staticmethod
    def send_tenant_sms(tenant, recipient, message, **kwargs):
        """
        New Sovereignty: Agnostic SMS Delivery.
        """
        provider = CommunicationFactory.get_sms_provider(tenant)
        return provider.send_sms(recipient, message, **kwargs)
