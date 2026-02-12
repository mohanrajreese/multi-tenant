import logging
try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    boto3 = None

from tenants.infrastructure.protocols_storage import IStorageProvider

logger = logging.getLogger(__name__)

class S3Provider(IStorageProvider):
    """
    Tier 58: AWS S3 Provider.
    For scalable cloud storage.
    """
    def __init__(self, config=None):
        self.config = config or {}
        self.bucket_name = self.config.get('bucket_name')
        self.region_name = self.config.get('region_name', 'us-east-1')
        self.aws_access_key_id = self.config.get('aws_access_key_id')
        self.aws_secret_access_key = self.config.get('aws_secret_access_key')
        self.custom_domain = self.config.get('custom_domain') # e.g. cdn.example.com

    def _get_client(self):
        if not boto3:
            raise ImportError("boto3 is not installed.")
        return boto3.client(
            's3',
            region_name=self.region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )

    def save(self, path, content, **kwargs):
        client = self._get_client()
        # Ensure content is at start if it's a file pointer
        if hasattr(content, 'seek'):
            content.seek(0)
            
        try:
            client.upload_fileobj(
                content, 
                self.bucket_name, 
                path, 
                ExtraArgs=kwargs.get('extra_args', {'ACL': 'private'})
            )
            return path
        except ClientError as e:
            logger.error(f"S3 Upload failed: {e}")
            raise e

    def delete(self, path):
        client = self._get_client()
        try:
            client.delete_object(Bucket=self.bucket_name, Key=path)
            return True
        except ClientError as e:
            logger.error(f"S3 Delete failed: {e}")
            return False

    def exists(self, path):
        client = self._get_client()
        try:
            client.head_object(Bucket=self.bucket_name, Key=path)
            return True
        except ClientError:
            return False

    def url(self, path):
        if self.custom_domain:
            return f"https://{self.custom_domain}/{path}"
        
        # Generator presigned URL if implicit access isn't public
        client = self._get_client()
        try:
            return client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': path},
                ExpiresIn=3600
            )
        except ClientError:
            return ""
