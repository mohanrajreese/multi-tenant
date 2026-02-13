from django.test import TestCase
from tenants.domain.models import Tenant
from tenants.infrastructure.hub import InfrastructureHub
from unittest.mock import patch, MagicMock

class WhatsAppIntegrationTest(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="Acme Corp", slug="acme")
        self.tenant.config = {
            "communication": {
                "whatsapp": {
                    "provider": "twilio",
                    "account_sid": "AC123",
                    "auth_token": "secret",
                    "from_number": "whatsapp:+123456789"
                }
            }
        }
        self.tenant.save()

    @patch('tenants.infrastructure.adapters.communication.providers.whatsapp.logger')
    def test_whatsapp_dispatch_mock(self, mock_logger):
        """
        Verify that InfrastructureHub correctly resolves the WhatsApp provider
        and falls back to logging when Twilio is not installed.
        """
        # Action
        provider = InfrastructureHub.whatsapp(self.tenant)
        success = provider.send_whatsapp(recipient="+987654321", message="Hello from Sovereign Engine!")
        
        # Assertions
        self.assertTrue(success)
        # Check if the mock log message was recorded
        mock_logger.info.assert_any_call("[WHATSAPP MOCK] To: +987654321, Body: Hello from Sovereign Engine!")
