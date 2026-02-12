from typing import Protocol, runtime_checkable, Any, Dict

@runtime_checkable
class IIdentityProvider(Protocol):
    """
    Tier 58: Identity Sovereignty Protocol.
    Abstracts SSO and Authentication checks.
    """
    def get_auth_url(self, redirect_uri: str, **kwargs: Any) -> str:
        """Return the URL to initiate the SSO flow."""
        ...

    def verify_token(self, token: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Verify the raw token from the client.
        Returns a standardized dict: {'email': ..., 'first_name': ..., 'last_name': ..., 'provider_uid': ...}
        """
        ...
