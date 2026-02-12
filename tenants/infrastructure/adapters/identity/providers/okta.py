import logging
from ..base import SSOProvider

logger = logging.getLogger(__name__)

class OktaSSOAdapter(SSOProvider):
    def __init__(self, config):
        self.client_id = config.get('client_id')
        self.org_url = config.get('org_url')

    def verify_token(self, token):
        logger.info(f"[Okta] Verifying token against {self.org_url}")
        # Mocking logic
        return {
            'email': 'user@okta-enterprise.com',
            'first_name': 'Okta',
            'last_name': 'Member',
            'provider_uid': 'okta_123'
        }

    def get_auth_url(self, redirect_uri):
        return f"{self.org_url}/oauth2/v1/authorize?client_id={self.client_id}&redirect_uri={redirect_uri}&response_type=id_token"
