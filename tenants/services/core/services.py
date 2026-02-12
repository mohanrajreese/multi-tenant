from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from .models import Tenant, Domain, Role, Membership


User = get_user_model()

class TenantService:

    @staticmethod
    def validate_onboarding_data(tenant_slug: str, domain_name: str, email: str):
        """
        Business Rule Validation. 
        Checks availability before starting a transaction.
        """
        if Tenant.objects.filter(slug=tenant_slug).exists():
            raise ValueError(f"Company URL '{tenant_slug}' is already taken.")
        
        if Domain.objects.filter(domain=domain_name).exists():
            raise ValueError(f"Domain '{domain_name}' is already registered.")
            
        if User.objects.filter(email=email).exists():
            raise ValueError(f"An account with email '{email}' already exists.")



    @classmethod
    @transaction.atomic
    def onboard_tenant(cls, tenant_name: str, admin_email: str, admin_password: str, domain_name: str = None, **kwargs) -> tuple:
        """
        Orchestrates the creation of a new Tenant ecosystem.
        """
        # 1. Normalize Input
        clean_slug = slugify(tenant_name)
        # 2. Get the platform base domain from settings (default: localhost)
        from .services_domain import DomainService
        base_domain = DomainService.get_base_domain()
        
        # If no domain provided, use the slug (e.g., acme.localhost)
        final_domain = domain_name or f"{clean_slug}.{base_domain}"
        # 2. Guard: Validate business rules
        cls.validate_onboarding_data(clean_slug, final_domain, admin_email)
        
        # 2.5 Find logic for a default "Starter" plan
        from .services_plan import PlanService
        default_plan = Plan.objects.filter(is_active=True).first()
        
        # 3. Create Entities
        tenant = Tenant.objects.create(
            name=tenant_name,
            slug=clean_slug,
            plan=default_plan,
            **kwargs
        )

        # Sync Quotas from Plan if it exists
        if default_plan:
            PlanService.apply_plan_to_tenant(tenant, default_plan)
        domain = Domain.objects.create(
            tenant=tenant,
            domain=final_domain,
            is_primary=True
        )
        admin_user = User.objects.create_superuser(
            username=admin_email, # Standard Django USERNAME_FIELD
            email=admin_email,
            password=admin_password
        )
        # 4. Create Default Admin Role for this Tenant
        admin_role, _ = Role.objects.get_or_create(
            tenant=tenant, 
            name="Admin"
        )
        
        # Assign default permissions to Admin
        from django.contrib.auth.models import Permission
        perms = Permission.objects.filter(codename__in=['add_membership', 'view_auditlog', 'add_product', 'view_domain', 'add_domain'])
        admin_role.permissions.add(*perms)
        # 5. Create Membership
        Membership.objects.create(
            user=admin_user,
            tenant=tenant,
            role=admin_role
        )
        # 4. Optional: Post-creation hooks (Send welcome email, setup defaults)
        from .services_email import TenantEmailService
        try:
            TenantEmailService.send_tenant_email(
                tenant=tenant,
                subject=f"Welcome to {tenant.name}!",
                message=f"Hello,\n\nYour organization {tenant.name} has been successfully created. You can access it at {final_domain}.",
                recipient_list=[admin_email]
            )
        except Exception as e:
            # We don't want to fail the whole onboarding if email fails, 
            # but in a real app, we'd log this.
            pass

        return tenant, admin_user
    @classmethod
    @transaction.atomic
    def purge_tenant_data(cls, tenant):
        """
        Compliance: Fully delete a tenant and ALL associated data.
        Leverages CASCADE and manual file cleanup.
        """
        import shutil
        from django.conf import settings
        from .conf import conf
        
        tenant_name = tenant.name
        tenant_id = str(tenant.id)
        
        # 1. Delete Database Records (Cascades)
        tenant.delete()

        # 2. Cleanup Media Files
        tenant_media_path = os.path.join(settings.MEDIA_ROOT, conf.STORAGE_PATH_PREFIX, tenant_id)
        if os.path.exists(tenant_media_path):
            shutil.rmtree(tenant_media_path)
            
        return f"Successfully purged all data and files for {tenant_name}."

    @classmethod
    def export_tenant_data(cls, tenant):
        """
        GDPR Portability: Export all tenant-specific data as a JSON dictionary.
        """
        from django.apps import apps
        from .models import TenantAwareModel
        
        export_data = {
            'tenant': {
                'name': tenant.name,
                'slug': tenant.slug,
                'config': tenant.config
            },
            'resources': {}
        }
        
        # Discover all TenantAwareModels and export their rows
        for model in apps.get_models():
            if issubclass(model, TenantAwareModel):
                # We skip AuditLog as it's massive, but could be included
                if model.__name__ == 'AuditLog': continue
                
                rows = model.objects.filter(tenant=tenant)
                export_data['resources'][model._meta.label] = [
                    # Dynamic serialization of basic fields
                    {f.name: str(getattr(row, f.name)) for f in model._meta.fields if f.name != 'tenant'}
                    for row in rows
                ]
                
        return export_data
