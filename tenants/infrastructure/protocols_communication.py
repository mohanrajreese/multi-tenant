from typing import Protocol, runtime_checkable, List, Optional, Any

@runtime_checkable
class IEmailProvider(Protocol):
    """
    Tier 57: Email Sovereignty Protocol.
    Abstracts email delivery mechanisms (SMTP, SendGrid, SES).
    """
    def send_email(self, recipient: str, subject: str, body: str, from_email: Optional[str] = None, **kwargs: Any) -> bool:
        """Send an email to a single recipient."""
        ...

@runtime_checkable
class ISMSProvider(Protocol):
    """
    Tier 57: SMS Sovereignty Protocol.
    Abstracts SMS delivery mechanisms (Twilio, SNS).
    """
    def send_sms(self, recipient: str, message: str, **kwargs: Any) -> bool:
        """Send an SMS to a single recipient."""
        ...
