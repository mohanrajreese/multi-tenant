from tenants.business.events.base import TenantRegisteredEvent
from tenants.business.events.dispatcher import subscribe
from tenants.business.use_cases.operations.services_email import TenantEmailService
from tenants.domain.models import Tenant
from tenants.infrastructure.database.schemas import SovereignSchemaManager

def handle_tenant_welcome_email(event: TenantRegisteredEvent):
    """Sends a welcome email when a new tenant is registered."""
    try:
        tenant = Tenant.objects.get(id=event.tenant_id)
        TenantEmailService.send_tenant_email(
            tenant=tenant,
            subject=f"Welcome to {event.tenant_name}!",
            message=f"Hello,\n\nYour organization {event.tenant_name} has been successfully created. You can access it at {event.domain_name}.",
            recipient_list=[event.admin_email]
        )
    except Exception:
        pass

def handle_tenant_schema_provisioning(event: TenantRegisteredEvent):
    """Apex Tier: Physically creates the PostgreSQL schema for the new tenant."""
    try:
        tenant = Tenant.objects.get(id=event.tenant_id)
        if tenant.isolation_mode == 'PHYSICAL':
            # Use slug for consistent schema naming (matches middleware)
            schema_name = tenant.slug.replace('-', '_')
            SovereignSchemaManager.provision_schema(schema_name)
            
            # In a real Apex setup, we would also run migrations for the new schema here:
            # from django.core.management import call_command
            # call_command('migrate', schema=schema_name, interactive=False)
    except Exception:
        pass

# Register all handlers here
subscribe(TenantRegisteredEvent, handle_tenant_welcome_email)
subscribe(TenantRegisteredEvent, handle_tenant_schema_provisioning)
