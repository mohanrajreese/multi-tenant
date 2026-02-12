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
    def onboard_tenant(cls, tenant_name: str, admin_email: str, admin_password: str, domain_name: str = None) -> tuple:
        """
        Orchestrates the creation of a new Tenant ecosystem.
        """
        # 1. Normalize Input
        clean_slug = slugify(tenant_name)
        # If no domain provided, use the slug (e.g., acme.localhost)
        final_domain = domain_name or f"{clean_slug}.localhost"
        # 2. Guard: Validate business rules
        cls.validate_onboarding_data(clean_slug, final_domain, admin_email)
        # 3. Create Entities
        tenant = Tenant.objects.create(
            name=tenant_name,
            slug=clean_slug
        )
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
        # TODO: Implement this
        # cls._setup_default_settings(tenant)
        return tenant, admin_user