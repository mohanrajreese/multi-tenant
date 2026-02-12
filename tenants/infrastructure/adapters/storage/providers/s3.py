from storages.backends.s3boto3 import S3Boto3Storage
import logging
from tenants.infrastructure.utils.context import get_current_tenant
from tenants.infrastructure.protocols.storage import IStorageProvider

logger = logging.getLogger(__name__)

class S3Provider(S3Boto3Storage, IStorageProvider):
    """
    Tier 58: AWS S3 Provider.
    For scalable cloud storage.
    Compatible with Django Storage API.
    """
    def __init__(self, config=None, **kwargs):
        self.config = config or {}
        # Map our config keys to S3Boto3Storage keys if needed, 
        # or rely on them being passed in kwargs or settings.
        # S3Boto3Storage uses settings.AWS_... by default.
        super().__init__(**kwargs)

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
