from django.contrib.auth import get_user_model
from tenants.domain.models import Membership
from tenants.infrastructure.adapters.identity.factory import IdentityFactory

User = get_user_model()

class IdentityService:
    """
    Apex Tier: Sovereign Identity Orchestration.
    Standardizes SSO authentication across Google, Okta, Azure AD, etc.
    """

    @staticmethod
    def authenticate_tenant_user(tenant, token):
        """
        Universal SSO Authentication.
        1. Resolve Provider via Factory
        2. Verify Token & Extract Standardized Profile
        3. Enforce Domain Whitelist
        4. Find or Create User/Membership
        """
        # Resolve the agnostic provider
        provider = IdentityFactory.get_provider(tenant)
        
        # Verify and extract standardized profile
        profile = provider.verify_token(token)
        email = profile.get('email')
        domain = email.split('@')[-1]

        # 1. Enforce Domain Whitelist (Sovereign Safety)
        sso_config = tenant.sso_config
        allowed_domains = sso_config.get('allowed_domains', [])
        if allowed_domains and domain not in allowed_domains:
            raise ValueError(f"Access denied: {domain} is not an authorized SSO domain for {tenant.name}.")

        # 2. Find/Create User (Atomically)
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email, 
                'first_name': profile.get('first_name', ''), 
                'last_name': profile.get('last_name', '')
            }
        )

        # 3. Ensure Membership in the Target Tenant
        membership, m_created = Membership.objects.get_or_create(
            tenant=tenant,
            user=user,
            defaults={'is_active': True}
        )

        return user

    @staticmethod
    def get_auth_url(tenant, redirect_uri):
        """
        Returns the correct SSO initiation URL for the tenant.
        """
        provider = IdentityFactory.get_provider(tenant)
        return provider.get_auth_url(redirect_uri)
