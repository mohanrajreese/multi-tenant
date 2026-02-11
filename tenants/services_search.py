from django.db.models import Q
from products.models import Product
from .models import Membership, AuditLog

class SearchService:
    @staticmethod
    def search(query):
        """
        Searches across Products, Memberships, and Audit Logs.
        Isolation is handled automatically by the TenantAwareModel manager.
        """
        results = {
            'products': [],
            'members': [],
            'logs': [],
            'query': query
        }
        
        if not query:
            return results
            
        # 1. Search Products
        results['products'] = Product.objects.filter(
            Q(name__icontains=query)
        )[:5]
        
        # 2. Search Members (by user email)
        results['members'] = Membership.objects.filter(
            Q(user__email__icontains=query) | Q(role__name__icontains=query)
        ).select_related('user', 'role')[:5]
        
        # 3. Search Audit Logs
        results['logs'] = AuditLog.objects.filter(
            Q(model_name__icontains=query) | 
            Q(object_repr__icontains=query) |
            Q(user__email__icontains=query)
        ).select_related('user')[:5]
        
        return results
