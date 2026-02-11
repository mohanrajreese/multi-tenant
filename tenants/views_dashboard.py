from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .decorators import tenant_permission_required
from django.utils.decorators import method_decorator
from products.models import Product
from .services_invitation import InvitationService
from .models import TenantInvitation, AuditLog, Domain

class DashboardHomeView(LoginRequiredMixin, View):
    def get(self, request):
        # Because of our TenantManager, Product.objects.all() 
        # is ALREADY filtered to only show this tenant's products!
        products_count = Product.objects.count()
        recent_products = Product.objects.order_by('-created_at')[:5]
        
        context = {
            'products_count': products_count,
            'recent_products': recent_products,
        }
        return render(request, 'dashboard/home.html', context)

class InviteUserView(LoginRequiredMixin, View):
    @method_decorator(tenant_permission_required('add_user')) # Using standard Django permission name or custom
    def get(self, request):
        invitations = TenantInvitation.objects.all().order_by('-created_at')
        return render(request, 'dashboard/invites.html', {'invitations': invitations})
    
    @method_decorator(tenant_permission_required('add_user'))
    def post(self, request):
        email = request.POST.get('email')
        role_name = request.POST.get('role', 'Member')
        
        try:
            InvitationService.create_invitation(
                tenant=request.tenant,
                invited_by=request.user,
                email=email,
                role_name=role_name
            )
            return redirect('dashboard_invites')
        except Exception as e:
            invitations = TenantInvitation.objects.all().order_by('-created_at')
            return render(request, 'dashboard/invites.html', {
                'invitations': invitations,
                'error': str(e)
            })

class ResendInviteView(LoginRequiredMixin, View):
    @method_decorator(tenant_permission_required('add_user'))
    def post(self, request, pk):
        try:
            InvitationService.resend_invitation(pk, request.tenant)
            return redirect('dashboard_invites')
        except Exception as e:
            # In a real app, use messages framework to show error
            return redirect('dashboard_invites')

class RevokeInviteView(LoginRequiredMixin, View):
    @method_decorator(tenant_permission_required('add_user'))
    def post(self, request, pk):
        try:
            InvitationService.revoke_invitation(pk, request.tenant)
            return redirect('dashboard_invites')
        except Exception as e:
            return redirect('dashboard_invites')

class AuditLogView(LoginRequiredMixin, View):
    @method_decorator(tenant_permission_required('view_audit_logs'))
    def get(self, request):
        logs = AuditLog.objects.all().select_related('user').order_by('-created_at')
        return render(request, 'dashboard/audit_logs.html', {'logs': logs})

class DomainManagementView(LoginRequiredMixin, View):
    @method_decorator(tenant_permission_required('manage_domains'))
    def get(self, request):
        domains = Domain.objects.all().order_by('-is_primary')
        return render(request, 'dashboard/domains.html', {'domains': domains})

    @method_decorator(tenant_permission_required('manage_domains'))
    def post(self, request):
        new_domain = request.POST.get('domain')
        if new_domain:
            Domain.objects.create(
                tenant=request.tenant,
                domain=new_domain,
                is_custom=True,
                status='PENDING'
            )
        return redirect('manage_domains')
