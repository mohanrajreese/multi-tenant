import logging
try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    boto3 = None

from ..base import EmailProvider

logger = logging.getLogger(__name__)

class SESProvider(EmailProvider):
    """
    Tier 57: AWS SES Email Provider.
    For high-scale transactional emails.
    """
    def __init__(self, config=None):
        self.config = config or {}
        self.region_name = self.config.get('region_name', 'us-east-1')
        self.aws_access_key_id = self.config.get('aws_access_key_id')
        self.aws_secret_access_key = self.config.get('aws_secret_access_key')
        
    def send_email(self, recipient, subject, body, from_email=None, **kwargs):
        if not boto3:
            logger.error("boto3 is not installed. Cannot use SESProvider.")
            return False

        try:
            client = boto3.client(
                'ses',
                region_name=self.region_name,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key
            )
            
            response = client.send_email(
                Source=from_email or self.config.get('from_email'),
                Destination={'ToAddresses': [recipient]},
                Message={
                    'Subject': {'Data': subject},
                    'Body': {'Text': {'Data': body}}
                }
            )
            logger.info(f"SES Email sent to {recipient} (MessageId: {response['MessageId']})")
            return True
        except ClientError as e:
            logger.error(f"SES specific error: {e.response['Error']['Message']}")
            return False
        except Exception as e:
            logger.error(f"Failed to send email via SES: {str(e)}")
            return False
