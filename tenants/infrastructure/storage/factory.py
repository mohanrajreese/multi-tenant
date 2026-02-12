from tenants.infrastructure.adapters.storage.factory import StorageFactory

def get_storage(tenant=None):
    """
    Delegates to the canonical StorageFactory in adapters.
    Maintains backward compatibility for models and legacy calls.
    """
    return StorageFactory.get_provider(tenant)

def get_tenant_storage():
    """
    A helper for FileField(storage=...) to enable dynamic runtime resolution.
    """
    return get_storage()
