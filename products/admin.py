from django.contrib import admin
from .models import Product
from tenants.admin_mixins import TenantAdminMixin

@admin.register(Product)
class ProductAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'sku', 'price', 'tenant')
    search_fields = ('name', 'sku')
