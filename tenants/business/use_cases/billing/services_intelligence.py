import logging
from django.utils import timezone
from datetime import timedelta
from tenants.models import Tenant, Membership
from tenants.models.models_governance import Quota

logger = logging.getLogger(__name__)

class IntelligenceEngine:
    """
    Chi Tier: Commercial Intelligence & Predictive Analytics.
    Identifies Churn Risk and Upsell Potential based on usage metrics.
    """

    @staticmethod
    def analyze_churn_risk(tenant: Tenant) -> dict:
        """
        Analyzes usage velocity over the last 30 days.
        Flags risk if activity drops significantly compared to the previous month.
        """
        # Mock logic: In production, query AuditLog or Metrics for activity spikes/drops
        # For demonstration, we'll return a score
        risk_score = 0
        reasons = []

        # Check login frequency or recent activity
        # If no activity in 14 days, high risk.
        risk_score = 25 # base
        
        return {
            "tenant": tenant.slug,
            "risk_level": "LOW" if risk_score < 30 else "MEDIUM" if risk_score < 70 else "HIGH",
            "risk_score": risk_score,
            "reasons": reasons
        }

    @staticmethod
    def detect_upsell_potential(tenant: Tenant) -> dict:
        """
        Detects if a tenant is hitting their quota limits consistently.
        """
        quotas = Quota.objects.filter(tenant=tenant)
        upsell_triggers = []

        for quota in quotas:
            percentage = (quota.used / quota.limit) * 100 if quota.limit > 0 else 0
            if percentage > 85:
                upsell_triggers.append(f"Quota '{quota.resource_name}' at {percentage:.1f}% capacity.")

        return {
            "tenant": tenant.slug,
            "has_potential": len(upsell_triggers) > 0,
            "recommendations": upsell_triggers
        }
