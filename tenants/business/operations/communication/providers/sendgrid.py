from ..base import EmailProvider
import logging

logger = logging.getLogger(__name__)

class SendGridProvider(EmailProvider):
    """
    Mock implementation of SendGrid provider.
    In a real app, this would use the sendgrid-python SDK.
    """
    def __init__(self, config):
        self.api_key = config.get('api_key')

    def send_email(self, recipient, subject, body, from_email=None, **kwargs):
        logger.info(f"[SendGrid] Sending email to {recipient} with subject '{subject}'")
        # Example SDK call logic would go here
        return True
