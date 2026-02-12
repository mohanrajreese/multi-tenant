from typing import Protocol, runtime_checkable, Any, Optional

@runtime_checkable
class ICacheProvider(Protocol):
    """
    Tier 62: Performance Sovereignty (Cache).
    Abstracts key-value store operations with tenant isolation.
    """
    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from the cache."""
        ...

    def set(self, key: str, value: Any, timeout: int = 300) -> bool:
        """Set a value in the cache."""
        ...

    def delete(self, key: str) -> bool:
        """Delete a value from the cache."""
        ...

@runtime_checkable
class IQueueProvider(Protocol):
    """
    Tier 62: Performance Sovereignty (Queue).
    Abstracts background task dispatch.
    """
    def enqueue(self, task_name: str, payload: Any, **kwargs: Any) -> str:
        """Dispatch a task to the background queue."""
        ...
