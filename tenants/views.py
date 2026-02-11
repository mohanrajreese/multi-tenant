from django.shortcuts import render, redirect
from django.views import View
from .services import TenantService
from .services_invitation import InvitationService
from .models import TenantInvitation

class IndexView(View):
    def get(self, request):
        if request.tenant:
            return redirect('/dashboard/')
        return render(request, 'index.html')

class OnboardView(View):
    def get(self, request):
        return render(request, 'onboard.html')
    
    def post(self, request):
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            tenant, admin_user = TenantService.onboard_tenant(
                tenant_name=name,
                admin_email=email,
                admin_password=password
            )
            # Find the primary domain to redirect
            primary_domain = tenant.domains.filter(is_primary=True).first()
            redirect_url = f"http://{primary_domain.domain}:8000/auth/login/"
            return redirect(redirect_url)
        except ValueError as e:
            return render(request, 'onboard.html', {'error': str(e)})

class AcceptInvitationView(View):
    def get(self, request, token):
        try:
            invitation = TenantInvitation.unscoped_objects.select_related('tenant').get(token=token)
            if invitation.is_accepted or invitation.is_expired():
                 return render(request, 'dashboard/invitation_error.html', {'message': "This invitation is no longer valid."})
            return render(request, 'dashboard/accept_invitation.html', {'invitation': invitation})
        except TenantInvitation.DoesNotExist:
             return render(request, 'dashboard/invitation_error.html', {'message': "Invalid invitation token."})

    def post(self, request, token):
        if not request.user.is_authenticated:
            return redirect(f'/auth/login/?next=/invite/accept/{token}/')
            
        try:
            tenant = InvitationService.accept_invitation(token, request.user)
            primary_domain = tenant.domains.filter(is_primary=True).first()
            return redirect(f"http://{primary_domain.domain}:8000/dashboard/")
        except Exception as e:
            return render(request, 'dashboard/invitation_error.html', {'message': str(e)})
