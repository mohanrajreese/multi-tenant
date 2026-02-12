import logging
from ..base import SSOProvider

logger = logging.getLogger(__name__)

class AzureSSOAdapter(SSOProvider):
    def __init__(self, config):
        self.client_id = config.get('client_id')
        self.tenant_id = config.get('tenant_id')

    def verify_token(self, token):
        logger.info(f"[Azure AD] Verifying token for tenant {self.tenant_id}")
        # Mocking logic
        return {
            'email': 'user@azure-enterprise.onmicrosoft.com',
            'first_name': 'Azure',
            'last_name': 'User',
            'provider_uid': 'azure_999'
        }

    def get_auth_url(self, redirect_uri):
        return f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/authorize?client_id={self.client_id}&redirect_uri={redirect_uri}&response_type=id_token"
