
from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import transaction, connection
from django.core.serializers import serialize, deserialize
from tenants.domain.models import Tenant, Domain, Membership, TenantInvitation
from tenants.domain.models.base import TenantAwareModel
from tenants.infrastructure.database.schemas import SovereignSchemaManager
from tenants.infrastructure.utils.security import SchemaSanitizer
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Tier 100: Migrates a tenant from LOGICAL (Shared) to PHYSICAL (Isolated) schema.'

    def add_arguments(self, parser):
        parser.add_argument('tenant_slug', type=str)

    def handle(self, *args, **options):
        slug = options['tenant_slug']
        try:
            tenant = Tenant.objects.get(slug=slug)
        except Tenant.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Tenant {slug} not found."))
            return

        if tenant.isolation_mode == 'PHYSICAL':
            self.stdout.write(self.style.WARNING(f"Tenant {slug} is already PHYSICAL."))
            return

        self.stdout.write(self.style.SUCCESS(f"Starting migration for {slug} -> PHYSICAL"))

        # 1. Identify Migratable Models
        # Exclude Core Identity/Routing models that must remain public
        EXCLUDED_MODELS = [Tenant, Domain, Membership, TenantInvitation]
        migratable_models = []
        
        for model in apps.get_models():
            if issubclass(model, TenantAwareModel) and model not in EXCLUDED_MODELS:
                # Check if it has a foreign key to Tenant (it should via TenantAwareModel)
                migratable_models.append(model)

        # 2. Extract Data from Public Schema
        data_packet = {}
        with transaction.atomic():
            for model in migratable_models:
                qs = model.objects.filter(tenant=tenant)
                count = qs.count()
                if count > 0:
                    json_data = serialize('json', qs)
                    data_packet[model._meta.label] = json_data
                    self.stdout.write(f"  Extracted {count} {model.__name__} records.")

        # 3. Provision New Schema
        schema_name = SchemaSanitizer.sanitize(tenant.slug)
        SovereignSchemaManager.provision_schema(schema_name)
        self.stdout.write(f"  Provisioned schema: {schema_name}")

        # 4. Restore Data to New Schema
        # We must manually activate the schema context
        from tenants.infrastructure.database.impl import SchemaManager
        old_schema = "public"
        
        try:
            SchemaManager.activate_schema(schema_name)
            
            with transaction.atomic():
                for label, json_data in data_packet.items():
                    for obj in deserialize('json', json_data):
                        # We must clear the ID if we want new IDs, but usually we want to preserve them.
                        # However, saving might conflict if sequences aren't updated.
                        # For MVP, we save directly.
                        obj.save(using='default') 
            
            self.stdout.write(self.style.SUCCESS("  Data restored to private schema."))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  Migration Failed: {e}"))
            # Cleanup?
            return
        finally:
            SchemaManager.activate_schema(old_schema)

        # 5. Update Tenant Record
        tenant.isolation_mode = 'PHYSICAL'
        tenant.save()
        
        # 6. (Optional) Cleanup Old Data
        # for model in migratable_models:
        #     model.objects.filter(tenant=tenant).delete()
        
        self.stdout.write(self.style.SUCCESS(f"Migration Complete: {slug} is now PHYSICAL."))
