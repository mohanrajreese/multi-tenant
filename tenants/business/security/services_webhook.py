import requests
import hmac
import hashlib
import json
from tenants.models import Webhook, WebhookEvent

class WebhookService:
    """
    Dispatches events to tenant-defined URLs.
    """

    @staticmethod
    def trigger_event(tenant, event_type, data):
        """
        Finds all active webhooks for a tenant interested in the event.
        """
        webhooks = Webhook.objects.filter(
            tenant=tenant, 
            is_active=True,
            events__contains=event_type
        )

        for webhook in webhooks:
            # 1. Prepare Payload
            payload = {
                'event': event_type,
                'tenant_id': str(tenant.id),
                'data': data
            }
            payload_json = json.dumps(payload)

            # 2. Sign Payload (Security)
            headers = {'Content-Type': 'application/json'}
            if webhook.secret:
                signature = hmac.new(
                    webhook.secret.encode(),
                    payload_json.encode(),
                    hashlib.sha256
                ).hexdigest()
                headers['X-Hub-Signature-256'] = f"sha256={signature}"

            # 3. Dispatch (In a real app, this would be a Celery task)
            try:
                response = requests.post(
                    webhook.target_url, 
                    data=payload_json, 
                    headers=headers,
                    timeout=5
                )
                
                # 4. Log the Delivery
                WebhookEvent.objects.create(
                    tenant=tenant,
                    webhook=webhook,
                    event_type=event_type,
                    payload=payload,
                    response_status=response.status_code,
                    response_body=response.text[:500]
                )
            except Exception as e:
                WebhookEvent.objects.create(
                    tenant=tenant,
                    webhook=webhook,
                    event_type=event_type,
                    payload=payload,
                    response_status=0,
                    response_body=str(e)[:500]
                )
