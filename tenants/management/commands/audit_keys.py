from django.core.management.base import BaseCommand
from tenants.business.use_cases.security.services_key_rotation import KeyRotationService

class Command(BaseCommand):
    help = 'Audits all tenant cryptographic keys and alerts if rotation is needed.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days', 
            type=int, 
            default=7, 
            help='Alert if expiration is within this many days.'
        )

    def handle(self, *args, **options):
        days = options['days']
        self.stdout.write(self.style.NOTICE(f'Starting key rotation audit (Threshold: {days} days)...'))
        
        count = KeyRotationService.audit_tenant_keys(threshold_days=days)
        
        if count > 0:
            self.stdout.write(self.style.SUCCESS(f'Audit complete. {count} rotation alerts triggered.'))
        else:
            self.stdout.write(self.style.SUCCESS('Audit complete. All keys are valid.'))
