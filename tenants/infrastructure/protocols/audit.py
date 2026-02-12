from typing import Protocol, runtime_checkable, Any, Dict

@runtime_checkable
class IAuditProvider(Protocol):
    """
    Tier 59: Audit Sovereignty Protocol.
    Abstracts compliance logging to various SIEMs (Splunk, Datadog, Database).
    """
    def log_event(self, tenant_id: str, actor_id: str, action: str, target_model: str, target_id: str, changes: Dict[str, Any], **kwargs: Any) -> bool:
        """Log a compliance event."""
        ...
