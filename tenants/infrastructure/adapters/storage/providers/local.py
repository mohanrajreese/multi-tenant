import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from tenants.infrastructure.protocols_storage import IStorageProvider

class LocalProvider(IStorageProvider):
    """
    Tier 58: Local Filesystem Provider.
    For development and on-premise deployments.
    """
    def __init__(self, config=None):
        self.config = config or {}
        # Allow overriding base location per tenant if needed
        location = self.config.get('location') or settings.MEDIA_ROOT
        base_url = self.config.get('base_url') or settings.MEDIA_URL
        self._storage = FileSystemStorage(location=location, base_url=base_url)

    def save(self, path, content, **kwargs):
        return self._storage.save(path, content)

    def delete(self, path):
        if self._storage.exists(path):
            self._storage.delete(path)
            return True
        return False

    def exists(self, path):
        return self._storage.exists(path)

    def url(self, path):
        return self._storage.url(path)
