import os
from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.conf import settings
from tenants.models import Tenant, Domain, Role, Membership, Plan
from tenants.business.exceptions import OnboardingConflictError
from tenants.business.events import dispatch, TenantRegisteredEvent

User = get_user_model()

class OnboardingService:
    """
    Business Tier: Multi-Tenant Onboarding Engine.
    Orchestrates the atomic creation of a new Tenant ecosystem.
    """

    @staticmethod
    def validate_onboarding_data(tenant_slug: str, domain_name: str, email: str):
        if Tenant.objects.filter(slug=tenant_slug).exists():
            raise OnboardingConflictError(f"Company URL '{tenant_slug}' is already taken.")
        
        if Domain.objects.filter(domain=domain_name).exists():
            raise OnboardingConflictError(f"Domain '{domain_name}' is already registered.")
            
        if User.objects.filter(email=email).exists():
            raise OnboardingConflictError(f"An account with email '{email}' already exists.")

    @classmethod
    @transaction.atomic
    def onboard_tenant(cls, tenant_name: str, admin_email: str, admin_password: str, domain_name: str = None, isolation_mode: str = 'LOGICAL', **kwargs) -> tuple:
        clean_slug = slugify(tenant_name)
        from tenants.business.core.services_domain import DomainService
        base_domain = DomainService.get_base_domain()
        
        final_domain = domain_name or f"{clean_slug}.{base_domain}"
        cls.validate_onboarding_data(clean_slug, final_domain, admin_email)
        
        from tenants.business.operations.services_plan import PlanService
        from tenants.models import Plan
        default_plan = Plan.objects.filter(is_active=True).first()
        
        tenant = Tenant.objects.create(
            name=tenant_name,
            slug=clean_slug,
            plan=default_plan,
            isolation_mode=isolation_mode,
            **kwargs
        )

        if default_plan:
            PlanService.apply_plan_to_tenant(tenant, default_plan)

        Domain.objects.create(
            tenant=tenant,
            domain=final_domain,
            is_primary=True
        )

        admin_user = User.objects.create_superuser(
            username=admin_email,
            email=admin_email,
            password=admin_password
        )

        admin_role, _ = Role.objects.get_or_create(
            tenant=tenant, 
            name="Admin"
        )
        
        from django.contrib.auth.models import Permission
        perms = Permission.objects.filter(codename__in=['add_membership', 'view_auditlog', 'add_product', 'view_domain', 'add_domain'])
        admin_role.permissions.add(*perms)

        Membership.objects.create(
            user=admin_user,
            tenant=tenant,
            role=admin_role
        )

        # Emit Domain Event for downstream side-effects (Email, Analytics, etc.)
        dispatch(TenantRegisteredEvent(
            tenant_id=str(tenant.id),
            tenant_name=tenant.name,
            admin_email=admin_email,
            domain_name=final_domain
        ))

        return tenant, admin_user
