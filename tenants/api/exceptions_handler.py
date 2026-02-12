from rest_framework import status
from rest_framework.views import exception_handler
from rest_framework.response import Response
from tenants.business.exceptions import SovereignError
from tenants.infrastructure.utils.resilience import CircuitBreakerError

def sovereign_exception_handler(exc, context):
    """
    Global exception handler for the Sovereign platform.
    Converts domain exceptions into standardized JSON responses.
    """
    # Call DRF's default exception handler first to get the standard error response.
    response = exception_handler(exc, context)

    # If it's one of our domain exceptions, wrap it in a standard format.
    if isinstance(exc, SovereignError):
        return Response({
            'status': 'error',
            'error': {
                'code': exc.code,
                'message': str(exc),
                'type': exc.__class__.__name__
            }
        }, status=exc.status_code)

    if isinstance(exc, CircuitBreakerError):
        return Response({
            'status': 'error',
            'error': {
                'code': 'circuit_open',
                'message': exc.message,
                'retry_after': exc.retry_after
            }
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE, headers={'Retry-After': str(exc.retry_after)})

    # If DRF already handled it (e.g. ValidationErrors), standardizing that too
    if response is not None:
        response.data = {
            'status': 'error',
            'error': {
                'code': 'api_error',
                'message': response.data
            }
        }
        return response

    return None
