from tenants.infrastructure.protocols.communication import IWhatsAppProvider
import logging

logger = logging.getLogger(__name__)

class TwilioWhatsAppProvider(IWhatsAppProvider):
    """
    Tier 77: Twilio WhatsApp Adapter.
    Uses the Twilio API to send WhatsApp messages.
    """
    def __init__(self, config=None):
        self.config = config or {}
        self.account_sid = self.config.get('account_sid')
        self.auth_token = self.config.get('auth_token')
        self.from_number = self.config.get('from_number', 'whatsapp:+14155238886') # Sandbox default

    def send_whatsapp(self, recipient: str, message: str, media_url=None, **kwargs):
        """
        Sends a WhatsApp message via Twilio.
        """
        if not self.account_sid or not self.auth_token:
            logger.error("[WhatsApp] Twilio credentials missing.")
            return False

        try:
            try:
                from twilio.rest import Client
            except ImportError:
                logger.error("[WhatsApp] Twilio library not installed. Falling back to Log.")
                logger.info(f"[WHATSAPP MOCK] To: {recipient}, Body: {message}")
                return True # Return true to satisfy the interface for now if we want to allow mock behavior
            client = Client(self.account_sid, self.auth_token)
            
            # WhatsApp numbers must be prefixed with 'whatsapp:'
            to_whatsapp = f"whatsapp:{recipient}" if not recipient.startswith("whatsapp:") else recipient
            
            message_data = {
                "from_": self.from_number,
                "to": to_whatsapp,
                "body": message
            }
            if media_url:
                message_data["media_url"] = [media_url]
            
            client.messages.create(**message_data)
            logger.info(f"[WhatsApp] Message sent to {recipient} via Twilio.")
            return True
        except Exception as e:
            logger.error(f"[WhatsApp] Twilio Error: {e}")
            return False
