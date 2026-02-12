from abc import ABC, abstractmethod

class EmailProvider(ABC):
    @abstractmethod
    def send_email(self, recipient, subject, body, from_email=None, **kwargs):
        """Send an email to a single recipient."""
        pass

class SMSProvider(ABC):
    @abstractmethod
    def send_sms(self, recipient, message, **kwargs):
        """Send an SMS to a single recipient."""
        pass
