from uuid import uuid4
from django.db import models

class TenantQuerySet(models.QuerySet):
    def for_tenant(self, tenant):
        return self.filter(tenant=tenant)

class TenantManager(models.Manager):
    def get_queryset(self):
        from tenants.infrastructure.utils.context import get_current_tenant
        tenant = get_current_tenant()
        
        queryset = TenantQuerySet(self.model, using=self._db)
        
        if tenant:
            return queryset.filter(tenant=tenant)
            
        return queryset

class TenantAwareModel(models.Model):
    """
    Abstract base model that automatically scopes queries to the current tenant.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='%(class)ss')
    
    objects = TenantManager()
    unscoped_objects = models.Manager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.tenant_id:
            from tenants.infrastructure.utils.context import get_current_tenant
            current_tenant = get_current_tenant()
            if current_tenant:
                self.tenant = current_tenant
        super().save(*args, **kwargs)
