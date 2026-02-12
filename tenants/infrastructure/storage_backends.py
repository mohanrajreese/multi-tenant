from storages.backends.s3boto3 import S3Boto3Storage
from .utils import get_current_tenant

class TenantAwareS3Storage(S3Boto3Storage):
    """
    Singularity Tier: High-Compliance Storage Isolation.
    Dynamically selects the S3 bucket and credentials based on the current tenant.
    """

    def __init__(self, *args, **kwargs):
        # We don't call super here yet, because we need the tenant context
        super().__init__(*args, **kwargs)

    @property
    def bucket_name(self):
        tenant = get_current_tenant()
        if tenant and tenant.storage_config:
            return tenant.storage_config.get('bucket_name', super().bucket_name)
        return super().bucket_name

    @property
    def access_key(self):
        tenant = get_current_tenant()
        if tenant and tenant.storage_config:
            return tenant.storage_config.get('access_key', super().access_key)
        return super().access_key

    @property
    def secret_key(self):
        tenant = get_current_tenant()
        if tenant and tenant.storage_config:
            return tenant.storage_config.get('secret_key', super().secret_key)
        return super().secret_key

class StorageRouter:
    """
    Utility to determine which storage engine to use.
    """
    @staticmethod
    def get_storage():
        tenant = get_current_tenant()
        if tenant and tenant.storage_config:
            return TenantAwareS3Storage()
        return None # Fallback to default
