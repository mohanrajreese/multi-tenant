from django.db import models
from tenants.models import Quota
from django.core.exceptions import ValidationError

class QuotaService:
    """
    Core engine for tracking and enforcing SaaS usage limits.
    """
    
    @staticmethod
    def check_quota(tenant, resource_name, increment=1):
        """
        Verifies if a tenant has enough quota to perform an action.
        Raises ValidationError if limit reached.
        """
        quota = Quota.objects.filter(tenant=tenant, resource_name=resource_name).first()
        
        # If no quota record exists, we assume UNLIMITED (Standard SaaS default)
        if not quota:
            return True
            
        # 0 means blocked/restricted unless specified
        if quota.limit_value > 0:
            if quota.current_usage + increment > quota.limit_value:
                raise ValidationError(
                    f"Quota exceeded for '{resource_name}'. "
                    f"Limit: {quota.limit_value}, Current: {quota.current_usage}"
                )
        
        return True

    @staticmethod
    def increment_usage(tenant, resource_name, amount=1):
        """
        Increments the usage count for a resource.
        """
        Quota.objects.filter(tenant=tenant, resource_name=resource_name).update(
            current_usage=models.F('current_usage') + amount
        )

    @staticmethod
    def decrement_usage(tenant, resource_name, amount=1):
        """
        Decrements the usage count for a resource.
        """
        Quota.objects.filter(tenant=tenant, resource_name=resource_name).update(
            current_usage=models.F('current_usage') - amount
        )
