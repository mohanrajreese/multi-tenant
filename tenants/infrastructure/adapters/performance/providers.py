from tenants.infrastructure.protocols.performance import ICacheProvider, IQueueProvider
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

class RedisNamespaceProvider(ICacheProvider):
    """
    Tier 62: Logical Cache Isolation.
    Prefixes all keys with tenant_id.
    """
    def __init__(self, tenant_id):
        self.tenant_id = tenant_id

    def _key(self, key):
        return f"{self.tenant_id}:{key}"

    def get(self, key, default=None):
        return cache.get(self._key(key), default)

    def set(self, key, value, timeout=300):
        # We assume value is picklable by Django cache
        cache.set(self._key(key), value, timeout)
        return True

    def delete(self, key):
        cache.delete(self._key(key))
        return True

class RedisClusterProvider(ICacheProvider):
    """
    Tier 62: Physical Cache Isolation.
    Connects to a specific Redis URL per tenant.
    """
    def __init__(self, config=None):
        self.config = config or {}
        self.redis_url = self.config.get('redis_url')
        # In a real app, we would initialize a redis client here
        # import redis
        # self.client = redis.from_url(self.redis_url)

    def get(self, key, default=None):
        # Mocking the physical connection
        # return self.client.get(key) or default
        logger.info(f"[RedisCluster] GET {key} from {self.redis_url}")
        return default

    def set(self, key, value, timeout=300):
        logger.info(f"[RedisCluster] SET {key} to {self.redis_url}")
        return True

    def delete(self, key):
        logger.info(f"[RedisCluster] DELETE {key} from {self.redis_url}")
        return True

class CeleryVHostProvider(IQueueProvider):
    """
    Tier 62: Tenant-Aware Task Dispatch.
    Routes tasks to specific queues or vhosts.
    """
    def __init__(self, config=None):
        self.config = config or {}
        self.queue_name = self.config.get('queue', 'default')

    def enqueue(self, task_name, payload, **kwargs):
        # Mocking Celery dispatch
        # celery_app.send_task(task_name, args=[payload], queue=self.queue_name)
        logger.info(f"[Celery] Dispatching {task_name} to queue {self.queue_name}")
        return "task_id_123"
