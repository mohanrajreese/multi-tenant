import logging
from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.contrib.auth.models import Permission

from tenants.domain.models import Tenant, Domain, Role, Membership, Plan
from tenants.business.exceptions import OnboardingConflictError
from tenants.business.events import dispatch, TenantRegisteredEvent
from tenants.business.dto import TenantOnboardingDTO
from tenants.infrastructure.conf import conf

User = get_user_model()
logger = logging.getLogger(__name__)

class OnboardTenantUseCase:
    """
    Tier 51: Clean Architecture Use Case.
    Orchestrates the atomic creation of a new Tenant ecosystem.
    Strictly depends on DTOs and localized domain logic.
    """

    @staticmethod
    def _validate_conflicts(data: TenantOnboardingDTO, slug: str, domain: str):
        if Tenant.objects.filter(slug=slug).exists():
            raise OnboardingConflictError(f"Company URL '{slug}' is already taken.")
        
        if Domain.objects.filter(domain=domain).exists():
            raise OnboardingConflictError(f"Domain '{domain}' is already registered.")
            
        if User.objects.filter(email=data.admin_email).exists():
            raise OnboardingConflictError(f"An account with email '{data.admin_email}' already exists.")

    @classmethod
    @transaction.atomic
    def execute(cls, data: TenantOnboardingDTO) -> tuple:
        """
        The singular entry point for onboarding a new tenant.
        Returns (Tenant, User).
        """
        clean_slug = slugify(data.tenant_name)
        
        # Determine Domain (Legacy logic support)
        from tenants.business.use_cases.core.services_domain import DomainService
        base_domain = conf.BASE_SAAS_DOMAIN
        final_domain = data.domain_name or f"{clean_slug}.{base_domain}"
        
        cls._validate_conflicts(data, clean_slug, final_domain)
        
        # 1. Create Core Tenant
        default_plan = Plan.objects.filter(is_active=True).first()
        tenant = Tenant.objects.create(
            name=data.tenant_name,
            slug=clean_slug,
            plan=default_plan,
            isolation_mode=data.isolation_mode,
            config=data.metadata
        )

        # 2. Provision Tenant Store (Database Sovereignty)
        if tenant.isolation_mode == 'PHYSICAL':
            from tenants.infrastructure.adapters.database.factory import DatabaseFactory
            # We use the tenant slug as the schema name (sanitized)
            schema_name = clean_slug.replace('-', '_')
            DatabaseFactory.get_provider().create_tenant_store(schema_name)

        # 3. Setup Plan
        if default_plan:
            from tenants.business.use_cases.operations.services_plan import PlanService
            PlanService.apply_plan_to_tenant(tenant, default_plan)

        # 4. Setup Domain
        Domain.objects.create(
            tenant=tenant,
            domain=final_domain,
            is_primary=True
        )

        # 5. Setup Admin Identity
        admin_user = User.objects.create_superuser(
            username=data.admin_email,
            email=data.admin_email,
            password=data.admin_password
        )

        admin_role, _ = Role.objects.get_or_create(
            tenant=tenant, 
            name="Admin"
        )
        
        perms = Permission.objects.filter(codename__in=[
            'add_membership', 'view_auditlog', 'add_product', 
            'view_domain', 'add_domain'
        ])
        admin_role.permissions.add(*perms)

        Membership.objects.create(
            user=admin_user,
            tenant=tenant,
            role=admin_role
        )

        # 6. Emit Domain Event
        dispatch(TenantRegisteredEvent(
            tenant_id=str(tenant.id),
            tenant_name=tenant.name,
            admin_email=data.admin_email,
            domain_name=final_domain
        ))

        logger.info(f"Sovereign Onboarding Success: {tenant.slug} (Admin: {admin_user.email})")
        return tenant, admin_user
