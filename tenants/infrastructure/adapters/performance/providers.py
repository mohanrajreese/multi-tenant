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
    Connects to a specific Redis URL/Cluster per tenant.
    """
    def __init__(self, config=None):
        self.config = config or {}
        self.redis_url = self.config.get('redis_url', 'redis://localhost:6379/0')

    def _get_client(self):
        try:
            import redis
            return redis.from_url(self.redis_url)
        except ImportError:
            logger.error("[RedisCluster] redis-py not installed. Using Log Mock.")
            return None

    def get(self, key, default=None):
        client = self._get_client()
        if not client:
            logger.info(f"[RedisCluster MOCK] GET {key} from {self.redis_url}")
            return default
            
        try:
            val = client.get(key)
            return val if val is not None else default
        except Exception as e:
            logger.error(f"[RedisCluster] GET Error: {e}")
            return default

    def set(self, key, value, timeout=300):
        client = self._get_client()
        if not client:
            logger.info(f"[RedisCluster MOCK] SET {key} to {self.redis_url}")
            return True
            
        try:
            client.setex(key, timeout, value)
            return True
        except Exception as e:
            logger.error(f"[RedisCluster] SET Error: {e}")
            return False

    def delete(self, key):
        client = self._get_client()
        if not client:
            logger.info(f"[RedisCluster MOCK] DELETE {key} from {self.redis_url}")
            return True
            
        try:
            client.delete(key)
            return True
        except Exception as e:
            logger.error(f"[RedisCluster] DELETE Error: {e}")
            return False

class CeleryVHostProvider(IQueueProvider):
    """
    Tier 62: Tenant-Aware Task Dispatch.
    Routes tasks to specific queues or vhosts for physical isolation.
    """
    def __init__(self, config=None):
        self.config = config or {}
        self.queue_name = self.config.get('queue', 'default')
        self.broker_url = self.config.get('broker_url') # e.g. amqp://tenant:pass@rabbitmq/vhost

    def enqueue(self, task_name, payload, **kwargs):
        try:
            from celery import current_app
            # We use the broker_url if provided for strictly isolated dispatch,
            # otherwise we route by queue name.
            dispatch_kwargs = {"queue": self.queue_name, "args": [payload]}
            if self.broker_url:
                # Advanced: Dynamic broker connection per task
                with current_app.connection_for_write(self.broker_url) as conn:
                    current_app.send_task(task_name, **dispatch_kwargs, connection=conn)
            else:
                current_app.send_task(task_name, **dispatch_kwargs)
                
            logger.info(f"[Celery] Dispatched {task_name} to queue {self.queue_name}")
            return "queued"
        except ImportError:
            logger.error("[Celery] Library not installed. Using Log Mock.")
            logger.info(f"[Celery MOCK] Dispatching {task_name} to queue {self.queue_name}")
            return "mock_id"
        except Exception as e:
            logger.error(f"[Celery] Enqueue Error: {e}")
            return None
