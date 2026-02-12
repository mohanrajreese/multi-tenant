from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from tenants.models import TenantInvitation, Role, Membership

class InvitationService:
    @staticmethod
    def create_invitation(tenant, invited_by, email, role_name="Member"):
        """
        Creates a new invitation for a user.
        """
        role = Role.objects.get(tenant=tenant, name=role_name)
        expires_at = timezone.now() + timedelta(days=7)
        
        invitation = TenantInvitation.objects.create(
            tenant=tenant,
            invited_by=invited_by,
            email=email,
            role=role,
            expires_at=expires_at
        )

        # Send the branded email
        from tenants.business.core.services_email import TenantEmailService
        try:
            TenantEmailService.send_tenant_email(
                tenant=tenant,
                subject=f"Inivitation to join {tenant.name}",
                message=f"Hello,\n\nYou have been invited to join {tenant.name} as a {role_name}.",
                recipient_list=[email]
            )
        except:
            pass
            
        return invitation

    @staticmethod
    @transaction.atomic
    def accept_invitation(token, user):
        """
        Accepts an invitation and creates the membership.
        """
        try:
            invitation = TenantInvitation.unscoped_objects.select_related('tenant', 'role').get(token=token)
        except TenantInvitation.DoesNotExist:
            raise ValueError("Invalid invitation token.")
        
        if invitation.is_accepted:
            raise ValueError("This invitation has already been accepted.")
            
        if invitation.is_expired():
            raise ValueError("This invitation has expired.")
            
        # 1. Create or Update Membership
        membership, created = Membership.objects.get_or_create(
            user=user,
            tenant=invitation.tenant,
            defaults={'role': invitation.role}
        )
        
        if not created:
            membership.role = invitation.role
            membership.save()
        
        # 2. Mark invitation as accepted
        invitation.is_accepted = True
        invitation.save()
        
        return invitation.tenant

    @staticmethod
    def resend_invitation(invitation_id, tenant):
        """
        Resets the expiry date and optionally regenerates the token.
        """
        invitation = TenantInvitation.objects.get(id=invitation_id, tenant=tenant)
        if invitation.is_accepted:
             raise ValueError("Cannot resend an already accepted invitation.")
             
        invitation.expires_at = timezone.now() + timedelta(days=7)
        invitation.save()
        
        # re-trigger email in real system
        return invitation

    @staticmethod
    def revoke_invitation(invitation_id, tenant):
        """
        Deletes the invitation.
        """
        invitation = TenantInvitation.objects.get(id=invitation_id, tenant=tenant)
        if invitation.is_accepted:
             raise ValueError("Cannot revoke an already accepted invitation.")
             
        invitation.delete()
