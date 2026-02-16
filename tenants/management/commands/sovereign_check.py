
from django.core.management.base import BaseCommand
from tenants.infrastructure.conf import conf
from django.core.management.color import no_style

class Command(BaseCommand):
    help = "Diagnoses the Sovereign Multi-Tenant Engine configuration status."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("\n🏛️ Sovereign Engine: Configuration Diagnostic Report\n"))
        
        report = conf.diagnose()
        
        total_missing = 0
        total_required_missing = 0
        
        for module, settings in report.items():
            self.stdout.write(self.style.MIGRATE_HEADING(f"Module: {module}"))
            
            for item in settings:
                status_color = self.style.SUCCESS
                if item['status'] == 'DEFAULT':
                    status_color = self.style.WARNING
                    if item['is_required']:
                        status_color = self.style.ERROR
                        total_required_missing += 1
                    total_missing += 1

                status_text = item['status']
                if item['is_required'] and item['status'] == 'DEFAULT':
                    status_text = "MISSING (REQUIRED)"

                self.stdout.write(
                    f"  {item['key']:30} -> " + 
                    status_color(f"[{status_text:15}]") + 
                    f" Value: {item['value']}"
                )
                self.stdout.write(self.style.HTTP_NOT_MODIFIED(f"     └─ {item['description']}"))
            self.stdout.write("")

        if total_required_missing > 0:
            self.stdout.write(self.style.ERROR(f"CRITICAL: {total_required_missing} required settings are missing! Deployment will fail."))
        elif total_missing > 0:
            self.stdout.write(self.style.WARNING(f"Note: {total_missing} settings are using default values. Review for production readiness."))
        else:
            self.stdout.write(self.style.SUCCESS("All systems go! Sovereign Engine is fully configured."))
        
        self.stdout.write("")
