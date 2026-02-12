import dns.resolver
from django.conf import settings
from .models import Domain

class DomainService:
    @staticmethod
    def get_base_domain():
        from django.conf import settings
        return getattr(settings, 'TENANT_BASE_DOMAIN', 'localhost')

    @staticmethod
    def verify_dns(domain_obj):
        """
        Hard-checks the DNS for a domain.
        Returns True if CNAME points to our BASE_SAAS_DOMAIN.
        """
        base_domain = DomainService.get_base_domain()
        try:
            # We look for CNAME records
            answers = dns.resolver.resolve(domain_obj.domain, 'CNAME')
            for rdata in answers:
                if base_domain in str(rdata.target):
                    return True
        except Exception:
            pass
        return False

    @classmethod
    def process_pending_domains(cls):
        """
        Logic for the Background Worker.
        Checks all PENDING domains and updates status.
        """
        pending = Domain.objects.filter(status='PENDING', is_custom=True)
        for domain in pending:
            if cls.verify_dns(domain):
                domain.status = 'ACTIVE'
                domain.save()
            # Note: We don't mark as FAILED immediately, as DNS propagation takes time.
