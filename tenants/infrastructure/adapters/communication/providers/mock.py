
import logging

logger = logging.getLogger(__name__)

class MockEmailProvider:
    def send_email(self, recipient, subject, body):
        logger.info(f"[SANDBOX] Mock Email dispatched to {recipient}. Subject: {subject}")
        return True

class MockSMSProvider:
    def send_sms(self, recipient, message):
        logger.info(f"[SANDBOX] Mock SMS dispatched to {recipient}. Msg: {message}")
        return True

class MockWhatsAppProvider:
    def send_whatsapp(self, recipient, message, media_url=None):
        logger.info(f"[SANDBOX] Mock WhatsApp dispatched to {recipient}. Msg: {message}")
        return True
