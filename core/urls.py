from django.contrib import admin
from django.urls import path, include
from tenants.views import IndexView, OnboardView, AcceptInvitationView
from tenants.views_dashboard import (
    DashboardHomeView, InviteUserView, ResendInviteView, 
    RevokeInviteView, AuditLogView, DomainManagementView, 
    GlobalSearchView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Public Routes
    path('', IndexView.as_view(), name='index'),
    path('onboard/', OnboardView.as_view(), name='onboard'),
    
    # Auth Routes
    path('auth/', include('users.urls')),
    
    # App Routes (Tenant Scoped)
    path('dashboard/', DashboardHomeView.as_view(), name='dashboard'),
    path('dashboard/invites/', InviteUserView.as_view(), name='dashboard_invites'),
    path('invite/accept/<uuid:token>/', AcceptInvitationView.as_view(), name='accept_invitation'),
    path('dashboard/invites/<uuid:pk>/resend/', ResendInviteView.as_view(), name='resend_invitation'),
    path('dashboard/invites/<uuid:pk>/revoke/', RevokeInviteView.as_view(), name='revoke_invitation'),
    path('dashboard/audit-logs/', AuditLogView.as_view(), name='audit_logs'),
    path('dashboard/domains/', DomainManagementView.as_view(), name='manage_domains'),
    path('dashboard/search/', GlobalSearchView.as_view(), name='global_search'),
    # path('products/', include('products.urls')),
]
