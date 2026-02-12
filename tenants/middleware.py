from .models import Domain
from .utils import set_current_tenant
from .cache import TenantCache
from django.shortcuts import render
from django.http import HttpResponsePermanentRedirect

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Get the raw host
        host = request.get_host().split(':')[0]

        # 2. Ultra-Fast Resolution (Cosmic Tier)
        # Try to get the domain from cache first
        cache_key = f"domain_resolution:{host}"
        domain = TenantCache.get(cache_key)
        
        if domain is None:
            try:
                domain = Domain.objects.select_related('tenant').get(
                    domain=host, 
                    status='ACTIVE'
                )
                # Store in cache for 1 hour
                TenantCache.set(cache_key, domain, timeout=3600)
            except Domain.DoesNotExist:
                domain = False # Use False to cache the 404/Null result
                TenantCache.set(cache_key, domain, timeout=300)

        tenant = domain.tenant if domain else None

        # 3. Global Context Setup
        request.tenant = tenant
        set_current_tenant(tenant)

        if tenant:
            # 4. IP Whitelisting (Cosmic Tier)
            if tenant.ip_whitelist:
                client_ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '')).split(',')[0].strip()
                if client_ip not in tenant.ip_whitelist:
                    return render(request, 'tenants/errors/base.html', {
                        'tenant': tenant,
                        'title': 'Forbidden',
                        'heading': 'Restricted Access',
                        'message': 'Your IP address is not authorized to access this organization.'
                    }, status=403)

            # 4.1 Deactivation Enforcement
            if not tenant.is_active:
                return render(request, 'tenants/errors/base.html', {
                    'tenant': tenant,
                    'title': 'Organization Inactive',
                    'heading': 'Organization Inactive',
                    'message': 'Please contact support to reactivate your account.'
                }, status=403)

            # 4.2 Membership Guard (Zenith Tier)
            if request.user.is_authenticated and not request.user.is_staff:
                if not request.path.startswith('/admin/') and not request.path.startswith('/onboard/'):
                    from .models import Membership
                    if not Membership.objects.filter(user=request.user, tenant=tenant, is_active=True).exists():
                        return render(request, 'tenants/errors/base.html', {
                            'tenant': tenant,
                            'title': 'Access Denied',
                            'heading': 'Access Denied',
                            'message': f'You are not an active member of {tenant.name}.'
                        }, status=403)

            # 4.3 Maintenance Mode Enforcement
            if tenant.is_maintenance:
                if not request.path.startswith('/admin/') and not request.GET.get('bypass_maintenance'):
                    return render(request, 'tenants/errors/base.html', {
                        'tenant': tenant,
                        'title': 'Under Maintenance',
                        'heading': f'{tenant.name} is under maintenance',
                        'message': "We'll be back shortly! Thanks for your patience."
                    }, status=503)

            # 4.4 Canonical Domain Redirect
            primary_domain = tenant.domains.filter(is_primary=True, status='ACTIVE').first()
            if primary_domain and primary_domain.domain != host and not host.endswith('.localhost'):
                scheme = request.is_secure() and "https" or "http"
                return HttpResponsePermanentRedirect(f"{scheme}://{primary_domain.domain}{request.path}")

        response = self.get_response(request)

        # 5. Dynamic CSP Headers (Cosmic Tier)
        if tenant and tenant.security_config:
            csp = tenant.security_config.get('content_security_policy')
            if csp:
                response['Content-Security-Policy'] = csp

        # 6. Cleanup
        set_current_tenant(None)

        return response
