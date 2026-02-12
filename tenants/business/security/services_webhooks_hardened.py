import hmac
import hashlib
import logging
from django.core.cache import cache
from tenants.models.models_billing import BillingEvent

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
