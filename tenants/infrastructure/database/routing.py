class TenantRouter:
    """
    Apex Tier: Database Router for Physical Isolation.
    Determines which models are 'Shared' (Public) vs 'Private' (Tenant Schema).
    """

    SHARED_MODELS = {'plan', 'tenant', 'domain'}
    PRIVATE_MODELS = {
        'role', 'membership', 'tenantinvitation', 
        'auditlog', 'quota', 'webhook', 'webhookevent',
        'tenantmetric', 'product', 'user'
    }

    def db_for_read(self, model, **hints):
        return 'default'

    def db_for_write(self, model, **hints):
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        In a real Apex setup, we would separate migrations by schema.
        For now, we allow all migrations on the default DB.
        """
        return True
