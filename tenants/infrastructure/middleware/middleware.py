from tenants.domain.models import Domain, Membership
from tenants.infrastructure.utils.context import set_current_tenant
from tenants.infrastructure.cache import TenantCache
from django.shortcuts import render
from django.http import HttpResponsePermanentRedirect, JsonResponse
from tenants.infrastructure.utils.security import SchemaSanitizer

class TenantResolutionMiddleware:
    """Layer 1: Identity & Context Resolution."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0]
        cache_key = f"domain_resolution:{host}"
        domain = TenantCache.get(cache_key)
        
        if domain is None:
            try:
                domain = Domain.objects.select_related('tenant').get(domain=host, status='ACTIVE')
                TenantCache.set(cache_key, domain, timeout=3600)
            except Domain.DoesNotExist:
                domain = False
                TenantCache.set(cache_key, domain, timeout=300)

        tenant = domain.tenant if domain else None
        request.tenant = tenant
        set_current_tenant(tenant)

        # Apex Tier: Physical Schema Isolation (Configurable)
        if tenant and tenant.isolation_mode == 'PHYSICAL':
            from tenants.infrastructure.database.schemas import SovereignSchemaManager
            # Tier 80: Use SchemaSanitizer for absolute identifier security
            schema_name = SchemaSanitizer.sanitize(tenant.slug)
            SovereignSchemaManager.set_active_schema(schema_name)
        else:
            # Default to Logical Isolation (using 'public'/default search path)
            from tenants.infrastructure.database.schemas import SovereignSchemaManager
            SovereignSchemaManager.set_active_schema('public')

        try:
            response = self.get_response(request)
        finally:
            set_current_tenant(None)

        return response

class TenantSecurityMiddleware:
    """Layer 2: Access Guards & Enforcement."""
    def __init__(self, get_response):
        self.get_response = get_response

    def _error_response(self, request, tenant, status, title, heading, message):
        """Tier 80: Headless Error Response Negotiator."""
        accept = request.META.get('HTTP_ACCEPT', '')
        
        if 'application/json' in accept or request.path.startswith('/api/'):
            return JsonResponse({
                "error": {
                    "code": title.upper().replace(' ', '_'),
                    "message": message,
                    "heading": heading
                }
            }, status=status)
            
        return render(request, 'tenants/errors/base.html', {
            'tenant': tenant, 'title': title, 'heading': heading,
            'message': message
        }, status=status)

    def __call__(self, request):
        tenant = getattr(request, 'tenant', None)
        if not tenant:
            return self.get_response(request)

        # 1. IP Whitelisting
        if tenant.ip_whitelist:
            client_ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '')).split(',')[0].strip()
            if client_ip not in tenant.ip_whitelist:
                return self._error_response(request, tenant, 403, 'Forbidden', 'Restricted Access', 'Your IP address is not authorized.')

        # 2. Status Enforcement
        if not tenant.is_active:
            return self._error_response(request, tenant, 403, 'Inactive', 'Organization Inactive', 'Contact support to reactivate.')

        # 3. Membership Guard
        if request.user.is_authenticated and not request.user.is_staff:
            if not request.path.startswith('/admin/') and not request.path.startswith('/onboard/'):
                if not Membership.objects.filter(user=request.user, tenant=tenant, is_active=True).exists():
                    return self._error_response(request, tenant, 403, 'Denied', 'Access Denied', f'You are not a member of {tenant.name}.')

        # 4. Maintenance
        if tenant.is_maintenance and not request.path.startswith('/admin/') and not request.GET.get('bypass_maintenance'):
            return self._error_response(request, tenant, 503, 'Maintenance', 'Under Maintenance', "We'll be back shortly!")

        return self.get_response(request)

class TenantPerformanceMiddleware:
    """Layer 3: Optimization & Security Headers."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tenant = getattr(request, 'tenant', None)
        host = request.get_host().split(':')[0]
        
        # 1. Canonical Redirect
        if tenant:
            primary_domain = tenant.domains.filter(is_primary=True, status='ACTIVE').first()
            if primary_domain and primary_domain.domain != host and not host.endswith('.localhost'):
                scheme = request.is_secure() and "https" or "http"
                return HttpResponsePermanentRedirect(f"{scheme}://{primary_domain.domain}{request.path}")

        response = self.get_response(request)

        # 2. CSP Headers
        if tenant and tenant.security_config:
            csp = tenant.security_config.get('content_security_policy')
            if csp:
                response['Content-Security-Policy'] = csp

        return response
