from django.contrib import admin
from .models import Tenant, Domain, Role, Membership, TenantInvitation, AuditLog, Quota
from .admin_mixins import TenantAdminMixin

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'is_maintenance', 'created_at')
    search_fields = ('name', 'slug')

@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('domain', 'tenant', 'is_primary', 'status')
    list_filter = ('status', 'is_primary')

@admin.register(Role)
class RoleAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'tenant')
    filter_horizontal = ('permissions',)

@admin.register(Membership)
class MembershipAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('user', 'tenant', 'role', 'is_active')
    list_filter = ('is_active', 'role')

@admin.register(TenantInvitation)
class TenantInvitationAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('email', 'tenant', 'role', 'is_accepted', 'expires_at')
    list_filter = ('is_accepted',)

@admin.register(AuditLog)
class AuditLogAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('action', 'model_name', 'object_repr', 'user', 'created_at')
    list_filter = ('action', 'model_name')
    readonly_fields = ('changes', 'ip_address', 'created_at')

@admin.register(Quota)
class QuotaAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('resource_name', 'limit_value', 'current_usage', 'tenant')
    list_filter = ('resource_name',)
