from dataclasses import dataclass, field
from typing import Optional, Dict, Any

@dataclass(frozen=True)
class TenantOnboardingDTO:
    """
    SoC: Data Transfer Object for Tenant Onboarding.
    Decouples the Business Layer from API serializers and DB models.
    """
    tenant_name: str
    admin_email: str
    admin_password: str
    domain_name: Optional[str] = None
    isolation_mode: str = 'LOGICAL'
    country_code: str = 'US'
    preferred_currency: str = 'USD'
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class BillingPlanDTO:
    """DTO for Plan-related orchestration."""
    plan_id: str
    name: str
    monthly_price: float
    yearly_price: float
    features: list = field(default_factory=list)
