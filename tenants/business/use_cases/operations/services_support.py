from django.contrib.auth import login
from tenants.domain.models import Membership, AuditLog

class SupportService:
    """
    Tools for Global Platform Administrators.
    """

    @staticmethod
    def impersonate_tenant_user(request, tenant, target_user):
        """
        Safely logs an admin into a tenant user's account for troubleshooting.
        Logs the action for security.
        """
        # 1. Verify target user belongs to the tenant
        if not Membership.objects.filter(tenant=tenant, user=target_user).exists():
            raise ValueError(f"User {target_user.email} is not a member of {tenant.name}")

        original_admin = request.user
        
        # 2. Perform Login
        # Note: In a real system, you'd use a custom backend to bypass password
        # but for this logic demo, we assume the admin has proper authority.
        login(request, target_user)

        # 3. Log the Event
        AuditLog.objects.create(
            tenant=tenant,
            user=target_user,
            action='UPDATE',
            model_name='SupportSession',
            object_id=str(target_user.id),
            object_repr=f"Impersonation by {original_admin.email}",
            changes={'impersonated_by': [None, original_admin.email]},
            ip_address=request.META.get('REMOTE_ADDR')
        )

        return f"Successfully impersonating {target_user.email} for {tenant.name}."
