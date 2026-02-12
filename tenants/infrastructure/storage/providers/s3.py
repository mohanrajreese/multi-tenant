from storages.backends.s3boto3 import S3Boto3Storage
from tenants.infrastructure.utils import get_current_tenant

class TenantAwareS3Storage(S3Boto3Storage):
    """
    Singularity Tier: High-Compliance S3 Isolation.
    Dynamically swaps buckets and credentials based on the current tenant.
    """
    def __init__(self, config=None, *args, **kwargs):
        self.config = config or {}
        super().__init__(*args, **kwargs)

    @property
    def bucket_name(self):
        tenant = get_current_tenant()
        if tenant and tenant.storage_config:
            return tenant.storage_config.get('bucket_name', super().bucket_name)
        return self.config.get('bucket_name', super().bucket_name)

    @property
    def access_key(self):
        tenant = get_current_tenant()
        if tenant and tenant.storage_config:
            return tenant.storage_config.get('access_key', super().access_key)
        return self.config.get('access_key', super().access_key)

    @property
    def secret_key(self):
        tenant = get_current_tenant()
        if tenant and tenant.storage_config:
            return tenant.storage_config.get('secret_key', super().secret_key)
        return self.config.get('secret_key', super().secret_key)
