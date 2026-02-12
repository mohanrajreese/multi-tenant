import logging
import jwt
from tenants.infrastructure.protocols_identity import IIdentityProvider

logger = logging.getLogger(__name__)

class OIDCProvider(IIdentityProvider):
    """
    Generic OIDC Provider (Works with Okta, Auth0, Keycloak).
    """
    def __init__(self, config=None):
        self.config = config or {}
        self.client_id = self.config.get('client_id')
        self.client_secret = self.config.get('client_secret')
        self.discovery_url = self.config.get('discovery_url')
        self.authorization_endpoint = self.config.get('authorization_endpoint')
        self.token_endpoint = self.config.get('token_endpoint')
        self.jwks_uri = self.config.get('jwks_uri')

    def get_auth_url(self, redirect_uri, **kwargs):
        return f"{self.authorization_endpoint}?client_id={self.client_id}&redirect_uri={redirect_uri}&response_type=code&scope=openid%20email%20profile"

    def verify_token(self, token, **kwargs):
        # In production this would use PyJWKClient to fetch keys from jwks_uri
        try:
            # We assume the token is already the ID Token (JWT)
            payload = jwt.decode(token, options={"verify_signature": False})
            return {
                'email': payload.get('email'),
                'first_name': payload.get('given_name', ''),
                'last_name': payload.get('family_name', ''),
                'provider_uid': payload.get('sub')
            }
        except Exception as e:
            logger.error(f"OIDC Verification Failed: {e}")
            raise ValueError("Invalid OIDC Token")

class SAMLProvider(IIdentityProvider):
    """
    Enterprise SAML 2.0 Provider.
    """
    def __init__(self, config=None):
        self.config = config or {}
        self.sso_url = self.config.get('sso_url')
        self.entity_id = self.config.get('entity_id')
        self.cert = self.config.get('cert')

    def get_auth_url(self, redirect_uri, **kwargs):
        return f"{self.sso_url}?SAMLRequest=MOCK_SAML_REQUEST&RelayState={redirect_uri}"

    def verify_token(self, token, **kwargs):
        # SAML response parsing is complex (python3-saml). 
        # Mocking extraction for architectural demo.
        return {
            'email': 'mock_saml_user@enterprise.com',
            'first_name': 'SAML',
            'last_name': 'User',
            'provider_uid': 'saml_12345'
        }
