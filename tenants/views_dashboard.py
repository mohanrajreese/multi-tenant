from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .decorators import tenant_permission_required
from django.utils.decorators import method_decorator
from products.models import Product
from .services_invitation import InvitationService
from .models import TenantInvitation, AuditLog, Domain
from .services_search import SearchService

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
    @method_decorator(tenant_permission_required('add_membership')) # Standard Django: add_<model_name>
    def get(self, request):
        invitations = TenantInvitation.objects.all().order_by('-created_at')
        return render(request, 'dashboard/invites.html', {'invitations': invitations})
    
    @method_decorator(tenant_permission_required('add_membership'))
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
    @method_decorator(tenant_permission_required('add_membership'))
    def post(self, request, pk):
        try:
            InvitationService.resend_invitation(pk, request.tenant)
            return redirect('dashboard_invites')
        except Exception as e:
            # In a real app, use messages framework to show error
            return redirect('dashboard_invites')

class RevokeInviteView(LoginRequiredMixin, View):
    @method_decorator(tenant_permission_required('add_membership'))
    def post(self, request, pk):
        try:
            InvitationService.revoke_invitation(pk, request.tenant)
            return redirect('dashboard_invites')
        except Exception as e:
            return redirect('dashboard_invites')

class AuditLogView(LoginRequiredMixin, View):
    @method_decorator(tenant_permission_required('view_auditlog'))
    def get(self, request):
        logs = AuditLog.objects.all().select_related('user').order_by('-created_at')
        return render(request, 'dashboard/audit_logs.html', {'logs': logs})

class DomainManagementView(LoginRequiredMixin, View):
    @method_decorator(tenant_permission_required('view_domain'))
    def get(self, request):
        domains = Domain.objects.all().order_by('-is_primary')
        return render(request, 'dashboard/domains.html', {'domains': domains})

    @method_decorator(tenant_permission_required('add_domain'))
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

class GlobalSearchView(LoginRequiredMixin, View):
    def get(self, request):
        query = request.GET.get('q', '')
        results = SearchService.search(query)
        
        # If it's an HTMX request, we return just the results fragment
        if request.headers.get('HX-Request') or request.GET.get('hx'):
             return render(request, 'dashboard/partials/search_results.html', results)
             
        return render(request, 'dashboard/search_full.html', results)
