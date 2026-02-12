from typing import Protocol, runtime_checkable, Any, Dict

@runtime_checkable
class IFeatureFlagProvider(Protocol):
    """
    Tier 66: Control Sovereignty Protocol.
    Abstracts feature toggles (Database, LaunchDarkly, Flagsmith).
    """
    def is_enabled(self, feature_key: str, tenant_id: str, default: bool = False, **kwargs: Any) -> bool:
        """Check if a feature is enabled for a tenant."""
        ...

    def get_all_flags(self, tenant_id: str) -> Dict[str, bool]:
        """Get all flags for a tenant."""
        ...
