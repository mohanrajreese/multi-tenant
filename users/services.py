from django.contrib.auth import get_user_model
from tenants.models import Membership, Role

User = get_user_model()

class UserService:
    @staticmethod
    def add_user_to_tenant(user, tenant, role_name="Member"):
        """
        Adds an existing user to a tenant with a specific role.
        """
        role, _ = Role.objects.get_or_create(tenant=tenant, name=role_name)
        membership, created = Membership.objects.get_or_create(
            user=user,
            tenant=tenant,
            defaults={'role': role}
        )
        if not created:
            membership.role = role
            membership.save()
        return membership

    @staticmethod
    def get_tenant_users(tenant):
        """
        Returns all users belonging to a specific tenant.
        """
        return User.objects.filter(memberships__tenant=tenant)
