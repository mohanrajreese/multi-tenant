from ..base import EmailProvider
from django.core.mail import get_connection, EmailMessage

class SMTPProvider(EmailProvider):
    def __init__(self, config):
        self.host = config.get('host')
        self.port = config.get('port')
        self.username = config.get('username')
        self.password = config.get('password')
        self.use_tls = config.get('use_tls', True)

    def send_email(self, recipient, subject, body, from_email=None, **kwargs):
        connection = get_connection(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            use_tls=self.use_tls
        )
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=from_email or self.username,
            to=[recipient],
            connection=connection
        )
        return email.send()
