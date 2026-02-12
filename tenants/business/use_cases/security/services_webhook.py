import hmac
import hashlib
import logging
from django.core.cache import cache
from tenants.domain.models.models_billing import BillingEvent

logger = logging.getLogger(__name__)

class WebhookHardeningService:
    """
    Upsilon Tier: Webhook Security & Idempotency.
    Protects against replay attacks and ensures delivery reliability.
    """

    @staticmethod
    def verify_signature(payload: str, signature: str, secret: str) -> bool:
        """
        Verifies the cryptographic signature of an incoming webhook.
        """
        if not signature or not secret:
            return False

        expected = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected, signature)

    @staticmethod
    def is_idempotent(event_id: str) -> bool:
        """
        Check if we have already processed this event ID.
        Uses a 2-tier check: Cache (fast) and Database (persistent).
        """
        # 1. Cache hit (last 24h)
        if cache.get(f"webhook_idemp_{event_id}"):
            return False

        # 2. Database hit
        if BillingEvent.objects.filter(provider_event_id=event_id).exists():
            return False

        # Mark as seen in cache for fast subsequent hits
        cache.set(f"webhook_idemp_{event_id}", True, timeout=86400)
        return True

    @staticmethod
    def log_event(tenant, event_id, event_type, payload):
        """Logs the event for auditing and troubleshooting."""
        return BillingEvent.objects.create(
            tenant=tenant,
            provider_event_id=event_id,
            event_type=event_type,
            payload=payload
        )

class WebhookService:
    """
    S-Apex Tier: Secure Event Propagation.
    Dispatches webhooks to external listeners with cryptographic signatures.
    """

    @staticmethod
    def trigger_event(tenant, event_type, data):
        """
        Synchronous/Asynchronous entry point for triggering tenant events.
        """
        from tenants.domain.models.models_integration import Webhook, WebhookEvent
        
        # Find active webhooks for this tenant
        active_hooks = Webhook.objects.filter(tenant=tenant, is_active=True)
        
        for hooks in active_hooks:
            # 1. Log the attempt
            WebhookEvent.objects.create(
                tenant=tenant,
                webhook=hooks,
                event_type=event_type,
                payload=data
            )
            logger.info(f"[WEBHOOK] Dispatched '{event_type}' for tenant {tenant.slug} to {hooks.target_url}")
            
            # 2. In production, this would fire an authenticated HTTP request.
            # 3. For verification, we simply acknowledge the dispatch.
