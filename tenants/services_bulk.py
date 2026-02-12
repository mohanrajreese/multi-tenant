from django.db import transaction
from .services_quota import QuotaService

class BulkImportService:
    """
    Standardized utility for bulk data orchestration.
    """

    @staticmethod
    @transaction.atomic
    def bulk_import(tenant, model_class, data_list, serializer_class):
        """
        Imports a list of objects while respecting quotas.
        """
        resource_name = f"max_{model_class._meta.model_name}s"
        count = len(data_list)
        
        # 1. Quota Validation
        QuotaService.check_quota(tenant, resource_name, increment=count)
        
        results = {
            'created': 0,
            'errors': []
        }
        
        # 2. Sequential Validation & Creation
        # We do this atomically so if one fails, the whole block fails (Enterprise Standard)
        for idx, item_data in enumerate(data_list):
            serializer = serializer_class(data=item_data, context={'request_tenant': tenant})
            if serializer.is_valid():
                obj = serializer.save(tenant=tenant)
                results['created'] += 1
                # Note: The 'automated_webhook_post_save' signal will fire 100 times here
                # providing real-time progress for the customer's integrations.
            else:
                results['errors'].append({'index': idx, 'errors': serializer.errors})
                # In atomic mode, we raise to rollback
                raise ValueError(f"Import failed at index {idx}: {serializer.errors}")

        # 3. Final Increment (Already handled by post_save signals, so we don't manual increment here)
        # BUT: Since our signals rely on thread-local context, we must ensure it's set
        # if this service is called from a background worker.
        
        return results
