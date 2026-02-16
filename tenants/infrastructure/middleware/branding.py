
from django.utils import timezone, translation
import pytz

class BrandingMiddleware:
    """Layer 4: Localization & Branding."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tenant = getattr(request, 'tenant', None)
        if tenant:
            # Timezone
            if tenant.timezone:
                try:
                    timezone.activate(pytz.timezone(tenant.timezone))
                except pytz.UnknownTimeZoneError:
                    pass
            
            # Locale
            if tenant.locale:
                translation.activate(tenant.locale)
                request.LANGUAGE_CODE = translation.get_language()
        
        response = self.get_response(request)
        
        if tenant:
            timezone.deactivate()
            translation.deactivate()
            
        return response
