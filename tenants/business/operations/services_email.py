from django.core.mail import send_mail
from django.conf import settings

class TenantEmailService:
    """
    Utility for sending branded emails on behalf of a tenant.
    """

    @staticmethod
    def send_tenant_email(tenant, subject, message, recipient_list, **kwargs):
        """
        Sends an email with tenant-specific branding.
        """
        brand_name = tenant.name
        support_email = tenant.support_email or getattr(settings, 'DEFAULT_FROM_EMAIL', 'support@platform.com')
        
        # Format the sender: "Acme Corp <support@acme.com>"
        from_email = f"{brand_name} <{support_email}>"
        
        # Add a branded footer to the message
        footer = f"\n\n---\nSent by {brand_name}\n"
        if tenant.website:
            footer += f"Visit us: {tenant.website}"
            
        full_message = message + footer
        
        return send_mail(
            subject=subject,
            message=full_message,
            from_email=from_email,
            recipient_list=recipient_list,
            **kwargs
        )
