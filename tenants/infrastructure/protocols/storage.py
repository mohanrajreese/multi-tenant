from typing import Protocol, runtime_checkable, Any, BinaryIO

@runtime_checkable
class IStorageProvider(Protocol):
    """
    Tier 58: Storage Sovereignty Protocol.
    Abstracts blob storage operations for tenant data isolation.
    """
    def save(self, path: str, content: BinaryIO, **kwargs: Any) -> str:
        """Save a file-like object to the storage backend. Returns the access URL or ID."""
        ...

    def delete(self, path: str) -> bool:
        """Delete a file from the storage backend."""
        ...
        
    def exists(self, path: str) -> bool:
        """Check if a file exists."""
        ...
        
    def url(self, path: str) -> str:
        """Get the public (or signed) URL for a file."""
        ...
