from rest_framework import status

class SovereignError(Exception):
    """Base exception for all Sovereign Platform business errors."""
    message = "An internal business error occurred."
    code = "sovereign_error"
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, message=None, code=None, status_code=None):
        if message: self.message = message
        if code: self.code = code
        if status_code: self.status_code = status_code
        super().__init__(self.message)

class QuotaExceededError(SovereignError):
    message = "Resource limit reached for your organization."
    code = "quota_exceeded"
    status_code = status.HTTP_429_TOO_MANY_REQUESTS

class TenantInactiveError(SovereignError):
    message = "Organization is currently inactive."
    code = "tenant_inactive"
    status_code = status.HTTP_403_FORBIDDEN

class DomainNotVerifiedError(SovereignError):
    message = "The requested domain has not been verified."
    code = "domain_unverified"
    status_code = status.HTTP_400_BAD_REQUEST

class OnboardingConflictError(SovereignError):
    message = "The provided company slug or domain is already in use."
    code = "onboarding_conflict"
    status_code = status.HTTP_409_CONFLICT

class IdentityProviderError(SovereignError):
    message = "Failed to communicate with the identity provider."
    code = "sso_provider_failure"
    status_code = status.HTTP_502_BAD_GATEWAY
