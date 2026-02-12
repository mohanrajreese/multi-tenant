import requests
import jwt
from django.contrib.auth import get_user_model
from .models import Membership

User = get_user_model()

class GoogleSSOService:
    """
    Singularity Tier: Identity Evolution.
    Handles Google OIDC authentication scoped to tenant-specific domains.
    """

    @staticmethod
    def verify_token(token, client_id):
        """
        Verifies the Google ID Token.
        In production, this would use google-auth-library.
        """
        # Mocking JWT verification for architectural demonstration
        try:
            # payload = id_token.verify_oauth2_token(token, requests.Request(), client_id)
            payload = jwt.decode(token, options={"verify_signature": False})
            return payload
        except Exception as e:
            raise ValueError(f"Invalid SSO Token: {str(e)}")

    @staticmethod
    def authenticate_tenant_user(tenant, token):
        """
        Authenticates a user for a specific tenant via Google SSO.
        1. Verify Token
        2. Check if email domain is allowed by tenant
        3. Find or Create user
        4. Ensure Membership exists
        """
        sso_config = tenant.sso_config
        if not sso_config:
            raise ValueError("Google SSO is not configured for this organization.")

        payload = GoogleSSOService.verify_token(token, sso_config.get('client_id'))
        email = payload.get('email')
        domain = email.split('@')[-1]

        # 1. Enforce Domain Whitelist
        allowed_domains = sso_config.get('allowed_domains', [])
        if allowed_domains and domain not in allowed_domains:
            raise ValueError(f"Access denied: {domain} is not an authorized SSO domain for {tenant.name}.")

        # 2. Find/Create User
        user, created = User.objects.get_or_create(
            email=email,
            defaults={'username': email, 'first_name': payload.get('given_name', ''), 'last_name': payload.get('family_name', '')}
        )

        # 3. Ensure Membership
        membership, m_created = Membership.objects.get_or_create(
            tenant=tenant,
            user=user,
            defaults={'is_active': True}
        )

        return user
