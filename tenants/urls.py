from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from .views.views import IndexView, OnboardView, AcceptInvitationView
from .views.views_dashboard import (
    DashboardHomeView, InviteUserView, ResendInviteView, 
    RevokeInviteView, AuditLogView, DomainManagementView, 
    GlobalSearchView
)
from .api.views import (
    AuditLogViewSet, OnboardingViewSet, TenantInvitationViewSet,
    RoleViewSet, DomainViewSet, TenantViewSet,
    AcceptInvitationAPIView, MembershipViewSet, 
    GlobalSearchAPIView, MeView, ChangePasswordView,
    PermissionViewSet, QuotaViewSet, HealthCheckAPIView,
    TenantSwitcherAPIView
)

# API v1 Router
router = DefaultRouter()
router.register(r'quotas', QuotaViewSet, basename='api_quota')
# Note: External apps (like products) can still register to this router 
# by importing it or we can provide a hook. For now, we'll keep it self-contained.
router.register(r'audit-logs', AuditLogViewSet, basename='api_audit_log')
router.register(r'members', MembershipViewSet, basename='api_membership')
router.register(r'invites', TenantInvitationViewSet, basename='api_invitation')
router.register(r'onboard', OnboardingViewSet, basename='api_onboarding')
from .api.views.views_support import ImpersonationViewSet

router.register(r'roles', RoleViewSet, basename='api_role')
router.register(r'permissions', PermissionViewSet, basename='api_permission')
router.register(r'domains', DomainViewSet, basename='api_domain')
router.register(r'settings', TenantViewSet, basename='api_settings')
router.register(r'support-impersonation', ImpersonationViewSet, basename='api_impersonation')

# --- Dynamic External App Registration ---
from .infrastructure.registry import APIRegistry
for prefix, viewset, basename in APIRegistry.get_viewsets():
    router.register(prefix, viewset, basename=basename)

urlpatterns = [
    # --- Dashboard Routes ---
    path('', IndexView.as_view(), name='index'),
    path('onboard/', OnboardView.as_view(), name='onboard'),
    path('dashboard/', DashboardHomeView.as_view(), name='dashboard'),
    path('dashboard/invites/', InviteUserView.as_view(), name='dashboard_invites'),
    path('invite/accept/<uuid:token>/', AcceptInvitationView.as_view(), name='accept_invitation'),
    path('dashboard/invites/<uuid:pk>/resend/', ResendInviteView.as_view(), name='resend_invitation'),
    path('dashboard/invites/<uuid:pk>/revoke/', RevokeInviteView.as_view(), name='revoke_invitation'),
    path('dashboard/audit-logs/', AuditLogView.as_view(), name='audit_logs'),
    path('dashboard/domains/', DomainManagementView.as_view(), name='manage_domains'),
    path('dashboard/search/', GlobalSearchView.as_view(), name='global_search'),

    # --- API v1 Routes ---
    path('api/v1/', include(router.urls)),
    path('api/v1/search/', GlobalSearchAPIView.as_view(), name='api_search'),
    path('api/v1/auth/me/', MeView.as_view(), name='api_me'),
    path('api/v1/auth/password/', ChangePasswordView.as_view(), name='api_password_change'),
    path('api/v1/auth-token/', obtain_auth_token, name='api_token'),
    path('api/v1/invites/accept/<uuid:token>/', AcceptInvitationAPIView.as_view(), name='api_accept_invitation'),
    path('api/v1/health/', HealthCheckAPIView.as_view(), name='api_health'),
    path('api/v1/auth/tenants/', TenantSwitcherAPIView.as_view(), name='api_tenant_switcher'),
    
    # OpenAPI Schema & Docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
