from .providers import RedisNamespaceProvider, RedisClusterProvider, CeleryVHostProvider

class CacheFactory:
    """
    Tier 62: Cache Resolution Factory.
    """
    @staticmethod
    def get_provider(tenant):
        config = tenant.config.get('cache', {})
        provider_type = config.get('provider', 'redis_namespace')
        
        if provider_type == 'redis_cluster':
            return RedisClusterProvider(config)
            
        return RedisNamespaceProvider(tenant.id)

class QueueFactory:
    """
    Tier 62: Queue Resolution Factory.
    """
    @staticmethod
    def get_provider(tenant):
        config = tenant.config.get('queue', {})
        # provider_type could be 'celery', 'sqs', 'rabbitmq'
        return CeleryVHostProvider(config)
