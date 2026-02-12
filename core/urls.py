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
    path('products/', include('products.urls')),
]

# API v1 Routing
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from products.api_views import ProductViewSet
from tenants.api_views import (
    AuditLogViewSet, 
    MembershipViewSet, 
    OnboardingViewSet, 
    TenantInvitationViewSet,
    GlobalSearchAPIView,
    MeView,
    RoleViewSet,
    PermissionViewSet,
    DomainViewSet,
    TenantViewSet,
    AcceptInvitationAPIView,
    ChangePasswordView
)

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='api_product')
router.register(r'audit-logs', AuditLogViewSet, basename='api_audit_log')
router.register(r'members', MembershipViewSet, basename='api_membership')
router.register(r'invites', TenantInvitationViewSet, basename='api_invitation')
router.register(r'onboard', OnboardingViewSet, basename='api_onboarding')
router.register(r'roles', RoleViewSet, basename='api_role')
router.register(r'permissions', PermissionViewSet, basename='api_permission')
router.register(r'domains', DomainViewSet, basename='api_domain')
router.register(r'settings', TenantViewSet, basename='api_settings')

urlpatterns += [
    path('api/v1/', include(router.urls)),
    path('api/v1/search/', GlobalSearchAPIView.as_view(), name='api_search'),
    path('api/v1/auth/me/', MeView.as_view(), name='api_me'),
    path('api/v1/auth/password/', ChangePasswordView.as_view(), name='api_password_change'),
    path('api/v1/auth-token/', obtain_auth_token, name='api_token'),
    path('api/v1/invites/accept/<uuid:token>/', AcceptInvitationAPIView.as_view(), name='api_accept_invitation'),
    
    # OpenAPI Schema & Docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
