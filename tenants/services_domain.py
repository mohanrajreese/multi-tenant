import dns.resolver
from django.conf import settings
from .models import Domain

class DomainService:
    BASE_SAAS_DOMAIN = "localhost" # In production, this would be your-saas.com

    @staticmethod
    def verify_dns(domain_obj):
        """
        Hard-checks the DNS for a domain.
        Returns True if CNAME points to our BASE_SAAS_DOMAIN.
        """
        try:
            # We look for CNAME records
            answers = dns.resolver.resolve(domain_obj.domain, 'CNAME')
            for rdata in answers:
                if DomainService.BASE_SAAS_DOMAIN in str(rdata.target):
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
