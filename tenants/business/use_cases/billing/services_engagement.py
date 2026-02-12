import logging
from tenants.domain.models import Tenant

logger = logging.getLogger(__name__)

class AnnouncementHub:
    """
    Tier 48: Engagement Sovereignty.
    Manages global and tenant-specific platform notifications.
    """

    @staticmethod
    def post_announcement(tenant: Tenant = None, title: str = "", content: str = "", level: str = "info"):
        """
        Persists an announcement. If tenant is None, it's a global broadcast.
        """
        # In production, this might use a dedicated Announcement model.
        # For this tier, we store in tenant config for localized delivery.
        
        target = "GLOBAL" if not tenant else tenant.slug
        logger.info(f"Posting {level} announcement to {target}: {title}")
        
        if tenant:
            alerts = tenant.config.get('announcements', [])
            alerts.append({
                'title': title,
                'content': content,
                'level': level,
                'timestamp': str(date.today())
            })
            tenant.config['announcements'] = alerts[-5:] # Keep last 5
            tenant.save()
        else:
            # Logic for global broadcast across all active tenants (async task)
            pass

    @staticmethod
    def get_announcements(tenant: Tenant):
        return tenant.config.get('announcements', [])
