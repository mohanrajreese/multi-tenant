import logging
from datetime import datetime, timedelta, date
from django.utils import timezone
from tenants.domain.models import Tenant
from tenants.infrastructure.hub import InfrastructureHub

logger = logging.getLogger(__name__)

class KeyRotationService:
    """
    Tier 69: Key Rotation Sovereignty.
    Audits cryptographic keys and triggers rotation workflows.
    """

    @staticmethod
    def audit_tenant_keys(threshold_days: int = 7):
        """
        Iterates through all tenants and identifies keys nearing expiration.
        """
        tenants = Tenant.objects.all()
        alerts_triggered = 0
        
        today = date.today()
        threshold_date = today + timedelta(days=threshold_days)

        for tenant in tenants:
            security_config = tenant.security_config or {}
            keys = security_config.get('keys', [])
            
            # If the config is a flat dict (backward compat for simpler tiers)
            if isinstance(keys, dict):
                keys = [keys]
            
            for key_meta in keys:
                expiry_str = key_meta.get('expiry_date')
                if not expiry_str:
                    continue
                
                try:
                    expiry_date = datetime.strptime(expiry_str, '%Y-%m-%d').date()
                except ValueError:
                    logger.warning(f"Invalid expiry date format for tenant {tenant.slug}: {expiry_str}")
                    continue

                if expiry_date <= threshold_date:
                    logger.info(f"Key for tenant {tenant.slug} (ID: {key_meta.get('id')}) expires on {expiry_date}. Triggering alert.")
                    KeyRotationService._trigger_alert(tenant, key_meta, expiry_date)
                    alerts_triggered += 1

        return alerts_triggered

    @staticmethod
    def _trigger_alert(tenant, key_meta, expiry_date):
        """
        Alerts the platform admin and tenant security contact.
        """
        subject = f"🚨 ACTION REQUIRED: Key Rotation for {tenant.name}"
        message = (
            f"The following cryptographic key is nearing expiration:\n\n"
            f"Tenant: {tenant.name} ({tenant.slug})\n"
            f"Key ID: {key_meta.get('id', 'N/A')}\n"
            f"Type: {key_meta.get('type', 'Unknown')}\n"
            f"Expiry Date: {expiry_date}\n\n"
            f"Please rotate this key in the provider console to avoid service interruption."
        )
        
        # 1. Notify Platform Admin (System Default)
        email_provider = InfrastructureHub.email(tenant)
        
        # Use support email if available, else fallback
        admin_email = tenant.support_email or "admin@platform.com"
        
        try:
            email_provider.send_email(
                recipient=admin_email,
                subject=subject,
                body=message
            )
            logger.info(f"Audit alert sent to {admin_email} for tenant {tenant.slug}")
        except Exception as e:
            logger.error(f"Failed to send rotation alert for tenant {tenant.slug}: {e}")
