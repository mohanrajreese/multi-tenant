import json
from django.core.serializers import serialize, deserialize
from django.apps import apps
from tenants.domain.models import Tenant, Membership, Domain, Quota, Role
from django.db import transaction

class TenantPortabilityService:
    """
    Sovereign Tier: Data Sovereignty.
    Enables full export/import of a tenant's entire ecosystem.
    """

    @staticmethod
    def export_organization(tenant):
        """
        Compiles all tenant-related data into a portable JSON package.
        """
        export_data = {
            'tenant': json.loads(serialize('json', [tenant]))[0],
            'domains': json.loads(serialize('json', tenant.domains.all())),
            'quotas': json.loads(serialize('json', tenant.quotas.all())),
            'memberships': json.loads(serialize('json', tenant.memberships.all())),
            'roles': json.loads(serialize('json', Role.objects.filter(tenant=tenant))),
        }

        # Dynamically discover and include all TenantAwareModel data
        for model in apps.get_models():
            if hasattr(model, 'tenant') and model not in [Tenant, Membership, Domain, Quota, Role]:
                related_data = model.objects.filter(tenant=tenant)
                if related_data.exists():
                    export_data[model._meta.label] = json.loads(serialize('json', related_data))

        return export_data

    @staticmethod
    @transaction.atomic
    def import_organization(data):
        """
        Reconstitutes an organization from a JSON package.
        """
        # Note: This is a complex operation that requires carefully handling 
        # ID re-mapping if importing into a system where some IDs already exist.
        # For simplicity, this demonstration handles the core serialization.
        
        objects = deserialize('json', json.dumps([data['tenant']]))
        for obj in objects:
            obj.save()
            
        # ... follow-up logic to restore related sets (domains, quotas, etc.)
        # and re-link foreign keys to the new tenant ID.
        
        return True
