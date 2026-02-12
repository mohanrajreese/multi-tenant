import logging
from django.core.management.base import BaseCommand
from django.core.management import call_command
from tenants.domain.models import Tenant
from tenants.infrastructure.database.schemas import SovereignSchemaManager
from django.db import connection

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Final Frontier: Orchestrates migrations across all physical tenant schemas."

    def add_arguments(self, parser):
        parser.add_argument('--tenant', type=str, help='Migrate a specific tenant slug only')
        parser.add_argument('--skip-public', action='store_true', help='Skip migration of the public schema')

    def handle(self, *args, **options):
        # 1. Migrate Public Schema (Shared tables: Plans, Tenants, etc.)
        if not options['skip_public']:
            self.stdout.write(self.style.SUCCESS("Migrating [PUBLIC] schema..."))
            call_command('migrate', interactive=False)

        # 2. Identify Tenants with Physical Isolation
        tenants = Tenant.objects.filter(isolation_mode='PHYSICAL')
        if options['tenant']:
            tenants = tenants.filter(slug=options['tenant'])

        self.stdout.write(self.style.WARNING(f"Orchestrating migrations for {tenants.count()} physical tenants..."))

        for tenant in tenants:
            schema_name = tenant.slug.replace('-', '_')
            self.stdout.write(f"  -> Migrating Tenant: {tenant.name} [{schema_name}]")
            
            try:
                # Switch connection to tenant schema
                SovereignSchemaManager.set_active_schema(schema_name)
                
                # Run migrations
                # In a real-world scenario, you might want to specify apps that are 'tenant-only'
                call_command('migrate', interactive=False)
                
                self.stdout.write(self.style.SUCCESS(f"     OK: {tenant.name}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"     FAILED: {tenant.name} - {str(e)}"))
            finally:
                # Always reset to public
                SovereignSchemaManager.set_active_schema('public')

        self.stdout.write(self.style.SUCCESS("Sovereign Migration Orchestration Complete."))
