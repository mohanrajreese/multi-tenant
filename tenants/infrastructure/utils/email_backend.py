from django.core.mail.backends.smtp import EmailBackend
from .utils import get_current_tenant

class TenantEmailBackend(EmailBackend):
    """
    Sovereign Tier: SMTP Isolation.
    Dynamically swaps SMTP credentials based on the current tenant's config.
    """

    def open(self):
        tenant = get_current_tenant()
        if tenant and tenant.smtp_config:
            # Override connection parameters with tenant-specific ones
            self.host = tenant.smtp_config.get('host', self.host)
            self.port = tenant.smtp_config.get('port', self.port)
            self.username = tenant.smtp_config.get('username', self.username)
            self.password = tenant.smtp_config.get('password', self.password)
            self.use_tls = tenant.smtp_config.get('use_tls', self.use_tls)
            self.use_ssl = tenant.smtp_config.get('use_ssl', self.use_ssl)
            
            # Reset the connection to use new credentials
            self.connection = None
            
        return super().open()
