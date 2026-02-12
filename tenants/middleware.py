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

        if tenant:
            # 4. Deactivation Enforcement
            if not tenant.is_active:
                from django.http import HttpResponseForbidden
                return HttpResponseForbidden(
                    "<h1>Organization Inactive</h1><p>Please contact support to reactivate your account.</p>"
                )

            # 5. Maintenance Mode Enforcement
            if tenant.is_maintenance:
                # We allow the Django Admin and a potential bypass param for developers
                if not request.path.startswith('/admin/') and not request.GET.get('bypass_maintenance'):
                    from django.http import HttpResponse
                    return HttpResponse(
                        f"<h1>{tenant.name} is under maintenance</h1><p>We'll be back shortly!</p>", 
                        status=503
                    )

            # 6. Canonical Domain Redirect
            # If the request is not on the primary domain, and a primary exists, redirect.
            # We skip this for local development or if no primary is set.
            primary_domain = tenant.domains.filter(is_primary=True, status='ACTIVE').first()
            if primary_domain and primary_domain.domain != host and not host.endswith('.localhost'):
                from django.http import HttpResponsePermanentRedirect
                scheme = request.is_secure() and "https" or "http"
                return HttpResponsePermanentRedirect(f"{scheme}://{primary_domain.domain}{request.path}")

        response = self.get_response(request)

        # 7. Cleanup
        set_current_tenant(None)

        return response
