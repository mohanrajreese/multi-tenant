from .models import Domain
from .utils import set_current_tenant
from django.http import Http404

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Get the raw host (e.g., 'acme.localhost' or 'mybrand.com')
        host = request.get_host().split(':')[0]

        # 2. Lookup the domain in our registry
        # We only look for ACTIVE domains
        try:
            domain = Domain.objects.select_related('tenant').get(
                domain=host, 
                status='ACTIVE'
            )
            tenant = domain.tenant
        except Domain.DoesNotExist:
            tenant = None

        # 3. Global Context Setup
        request.tenant = tenant
        set_current_tenant(tenant)

        response = self.get_response(request)

        # 4. Cleanup
        set_current_tenant(None)

        return response
