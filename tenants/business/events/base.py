from dataclasses import dataclass, field, KW_ONLY
from datetime import datetime
from uuid import uuid4

@dataclass(frozen=True)
class DomainEvent:
    """Base class for all domain events."""
    _: KW_ONLY
    event_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass(frozen=True)
class TenantRegisteredEvent(DomainEvent):
    tenant_id: str
    tenant_name: str
    admin_email: str
    domain_name: str
