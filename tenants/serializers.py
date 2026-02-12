from rest_framework import serializers
from .models import AuditLog, Membership, TenantInvitation, Tenant, Role, Domain, Quota
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']
        read_only_fields = ['id', 'email']

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'content_type']

class RoleSerializer(serializers.ModelSerializer):
    permission_ids = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        source='permissions',
        many=True,
        required=False,
        write_only=True
    )
    permission_details = PermissionSerializer(source='permissions', many=True, read_only=True)

    class Meta:
        model = Role
        fields = ['id', 'name', 'permission_ids', 'permission_details']

class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = [
            'id', 'name', 'slug', 'logo', 
            'primary_color', 'secondary_color', 
            'support_email', 'website', 
            'is_maintenance', 'config', 'created_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at']

class DomainSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Domain
        fields = ['id', 'domain', 'is_primary', 'is_custom', 'status', 'status_display', 'created_at']
        read_only_fields = ['id', 'created_at', 'status']

class AuditLogSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = ['id', 'action', 'model_name', 'object_repr', 'changes', 'user_email', 'user_name', 'ip_address', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_user_name(self, obj):
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.email
        return "System"

class OnboardingSerializer(serializers.Serializer):
    """
    Handles the public tenant creation process via API.
    """
    tenant_name = serializers.CharField(max_length=100)
    admin_email = serializers.EmailField()
    admin_password = serializers.CharField(write_only=True)
    domain_name = serializers.CharField(max_length=255, required=False)

    # Branding / Contact (Optional)
    logo = serializers.ImageField(required=False)
    primary_color = serializers.CharField(max_length=7, required=False)
    secondary_color = serializers.CharField(max_length=7, required=False)
    support_email = serializers.EmailField(required=False)
    website = serializers.URLField(required=False)

    def validate_tenant_name(self, value):
        from django.utils.text import slugify
        slug = slugify(value)
        if Tenant.objects.filter(slug=slug).exists():
            raise serializers.ValidationError(f"Organization '{value}' is already taken.")
        return value

class TenantInvitationSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.name', read_only=True)
    invited_by_email = serializers.EmailField(source='invited_by.email', read_only=True)

    class Meta:
        model = TenantInvitation
        fields = ['id', 'email', 'role', 'role_name', 'token', 'invited_by_email', 'is_accepted', 'expires_at']
        read_only_fields = ['id', 'token', 'is_accepted', 'invited_by_email']

class MembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)

    class Meta:
        model = Membership
        fields = ['id', 'user_email', 'role', 'role_name', 'is_active', 'joined_at']
        read_only_fields = ['id', 'joined_at', 'user_email', 'role_name']

class QuotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quota
        fields = ['id', 'resource_name', 'limit_value', 'current_usage']
        read_only_fields = ['id', 'current_usage']
