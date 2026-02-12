import logging
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model
from tenants.infrastructure.utils.context import get_current_tenant

User = get_user_model()
logger = logging.getLogger(__name__)

class AdminImpersonationMiddleware(MiddlewareMixin):
    """
    Omega Tier: Secure Support Impersonation.
    Allows staff to act as a tenant user with a mandatory audit trail.
    """
    
    def process_request(self, request):
        # 1. Check if an impersonation session is active
        impersonator_id = request.session.get('impersonator_id')
        
        if impersonator_id and request.user.is_authenticated:
            # The current 'request.user' is actually the target user we are impersonating
            # We store the real admin (the impersonator) for the audit trail
            try:
                impersonator = User.objects.get(id=impersonator_id)
                if not impersonator.is_staff:
                    # Security breach attempt: Clear session
                    del request.session['impersonator_id']
                    return

                # Inject impersonator context for use in Audit Logs
                from tenants.infrastructure.utils.context import set_current_impersonator
                set_current_impersonator(impersonator)
                
                request.impersonator = impersonator
                request.is_impersonating = True
                
                logger.info(f"Staff member {impersonator.email} IS IMPERSONATING {request.user.email}")
                
            except User.DoesNotExist:
                del request.session['impersonator_id']
