from django.db import models
from tenants.models import TenantAwareModel
from tenants.infrastructure.storage.utils import tenant_storage_path
from tenants.infrastructure.storage.factory import get_tenant_storage

class Product(TenantAwareModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(
        upload_to=tenant_storage_path, 
        storage=get_tenant_storage,
        null=True, 
        blank=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - ${self.price}"


