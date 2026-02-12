import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from tenants.infrastructure.protocols.storage import IStorageProvider

class LocalProvider(FileSystemStorage, IStorageProvider):
    """
    Tier 58: Local Filesystem Provider.
    For development and on-premise deployments.
    Compatible with Django Storage API.
    """
    def __init__(self, config=None, *args, **kwargs):
        self.config = config or {}
        location = self.config.get('location') or settings.MEDIA_ROOT
        base_url = self.config.get('base_url') or settings.MEDIA_URL
        super().__init__(location=location, base_url=base_url, *args, **kwargs)
        
    def save(self, name, content, max_length=None):
        return super().save(name, content, max_length=max_length)
