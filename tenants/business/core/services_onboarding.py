import os
from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.conf import settings
from tenants.models import Tenant, Domain, Role, Membership, Plan

User = get_user_model()

class OnboardingService:
    """
    Business Tier: Multi-Tenant Onboarding Engine.
    Orchestrates the atomic creation of a new Tenant ecosystem.
    """

    @staticmethod
    def validate_onboarding_data(tenant_slug: str, domain_name: str, email: str):
        if Tenant.objects.filter(slug=tenant_slug).exists():
            raise ValueError(f"Company URL '{tenant_slug}' is already taken.")
        
        if Domain.objects.filter(domain=domain_name).exists():
            raise ValueError(f"Domain '{domain_name}' is already registered.")
            
        if User.objects.filter(email=email).exists():
            raise ValueError(f"An account with email '{email}' already exists.")

    @classmethod
    @transaction.atomic
    def onboard_tenant(cls, tenant_name: str, admin_email: str, admin_password: str, domain_name: str = None, **kwargs) -> tuple:
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

        from tenants.business.operations.services_email import TenantEmailService
        try:
            TenantEmailService.send_tenant_email(
                tenant=tenant,
                subject=f"Welcome to {tenant.name}!",
                message=f"Hello,\n\nYour organization {tenant.name} has been successfully created. You can access it at {final_domain}.",
                recipient_list=[admin_email]
            )
        except Exception:
            pass

        return tenant, admin_user
