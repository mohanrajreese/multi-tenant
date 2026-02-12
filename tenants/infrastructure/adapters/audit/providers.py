from tenants.infrastructure.protocols.audit import IAuditProvider
from tenants.domain.models import AuditLog
import logging
import json

logger = logging.getLogger(__name__)

class DatabaseAuditProvider(IAuditProvider):
    """
    Tier 59: Default Database Logging.
    Persistence via Django ORM.
    """
    def log_event(self, tenant_id, actor_id, action, target_model, target_id, changes, **kwargs):
        # We need to resolve objects from IDs if we want to keep foreign keys,
        # or we just store raw IDs if we want to be pure.
        # The current AuditLog model has ForeignKeys (tenant, user).
        # For the provider, we might need to fetch them.
        
        # However, to avoid circular deps or complex lookups here, 
        # we assume kwargs might pass the actual objects if available, 
        # or we rely on the caller to have resolved them.
        
        # But wait, the Protocol signature uses IDs.
        # Let's adjust implementation to handle both or fetch.
        
        from tenants.domain.models import Tenant
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        tenant = kwargs.get('tenant') 
        if not tenant and tenant_id:
            tenant = Tenant.objects.filter(id=tenant_id).first()
            
        user = kwargs.get('user')
        if not user and actor_id and actor_id != 'system':
            user = User.objects.filter(id=actor_id).first()
            
        AuditLog.objects.create(
            tenant=tenant,
            user=user,
            impersonator=kwargs.get('impersonator'),
            action=action,
            model_name=target_model,
            object_id=target_id,
            object_repr=kwargs.get('object_repr', ''),
            changes=changes
        )
        return True

class SplunkProvider(IAuditProvider):
    """
    Tier 59: Enterprise SIEM Logging (Splunk).
    """
    def __init__(self, config=None):
        self.config = config or {}
        self.host = self.config.get('host', 'splunk.enterprise.com')
        self.token = self.config.get('token')

    def log_event(self, tenant_id, actor_id, action, target_model, target_id, changes, **kwargs):
        payload = {
            "tenant_id": str(tenant_id),
            "actor_id": str(actor_id),
            "action": action,
            "target": f"{target_model}:{target_id}",
            "changes": changes,
            "meta": kwargs,
            "sourcetype": "sovereign_audit",
            "event": "compliance_log"
        }
        
        import requests
        try:
            # Splunk HEC usually lives at /services/collector
            url = f"{self.host}/services/collector"
            headers = {"Authorization": f"Splunk {self.token}"}
            requests.post(url, json=payload, headers=headers, timeout=2)
            return True
        except Exception as e:
            logger.error(f"[Splunk] Delivery Error: {e}")
            return False

class DatadogProvider(IAuditProvider):
    """
    Tier 59: Datadog Events.
    """
    def log_event(self, tenant_id, actor_id, action, target_model, target_id, changes, **kwargs):
        # Datadog Events API V1
        import requests
        
        api_key = self.config.get('api_key')
        if not api_key:
            return False
            
        url = f"https://api.datadoghq.com/api/v1/events?api_key={api_key}"
        
        payload = {
            "title": f"Audit: {action} on {target_model}",
            "text": f"User {actor_id} performed {action} on {target_model}:{target_id}. Changes: {json.dumps(changes)}",
            "tags": [f"tenant:{tenant_id}", "source:sovereign_engine"],
            "alert_type": "info"
        }
        
        try:
            requests.post(url, json=payload, timeout=2)
            return True
        except Exception as e:
            logger.error(f"[Datadog] Delivery Error: {e}")
            return False
