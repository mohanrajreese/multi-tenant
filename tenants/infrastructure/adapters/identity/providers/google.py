import jwt
from ..base import SSOProvider

class GoogleSSOAdapter(SSOProvider):
    def __init__(self, config):
        self.client_id = config.get('client_id')
        self.client_secret = config.get('client_secret')

    def verify_token(self, token):
        # In a real app, use: google.oauth2.id_token.verify_oauth2_token(token, requests.Request(), self.client_id)
        # Mocking for architectural demonstration
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            return {
                'email': payload.get('email'),
                'first_name': payload.get('given_name', ''),
                'last_name': payload.get('family_name', ''),
                'provider_uid': payload.get('sub')
            }
        except Exception as e:
            raise ValueError(f"Google SSO Token Error: {str(e)}")

    def get_auth_url(self, redirect_uri):
        return f"https://accounts.google.com/o/oauth2/v2/auth?client_id={self.client_id}&redirect_uri={redirect_uri}&response_type=code&scope=email%20profile"
