from django.conf import settings
from typing import Any

class SovereignConfig:
    """
    SoC: Internal Configuration Hub.
    Centralizes all engine defaults and overrides with TENANT_ prefixing.
    Provides diagnostic capabilities to detect missing environment variables.
    """
    PREFIX = 'TENANT_'

    # Settings grouped by module for diagnostics
    MODULE_MAP = {
        'CORE': [
            'BASE_SAAS_DOMAIN', 'MANAGED_APPS', 'DEFAULT_ISOLATION', 'MIGRATION_PARALLELISM',
            'MASTER_SECRET'
        ],
        'STORAGE': ['STORAGE_PATH_PREFIX'],
        'RESILIENCE': ['CIRCUIT_BREAKER_THRESHOLD', 'CIRCUIT_BREAKER_RESET_TIMEOUT', 'TRACING_ENABLED'],
        'GOVERNANCE': ['QUOTA_STRICT_MODE', 'AUDIT_LOG_RETENTION_DAYS'],
        'BILLING': ['BILLING_PROVIDER_DEFAULT'],
        'COMMUNICATION': ['EMAIL_PROVIDER_DEFAULT', 'SMS_PROVIDER_DEFAULT', 'WHATSAPP_PROVIDER_DEFAULT'],
        'PERFORMANCE': ['CACHE_ISOLATION_STRATEGY', 'QUEUE_ISOLATION_STRATEGY'],
        'SEARCH': ['SEARCH_PROVIDER_DEFAULT', 'ELASTICSEARCH_URL'],
    }

    # Metadata for diagnostic details
    METADATA = {
        'BASE_SAAS_DOMAIN': 'Primary domain for the SaaS platform (e.g., localhost or saas.com).',
        'STORAGE_PATH_PREFIX': 'Subdirectory prefix for all tenant-specific file uploads.',
        'CIRCUIT_BREAKER_THRESHOLD': 'Consecutive failures before tripping the circuit for a specific provider.',
        'TRACING_ENABLED': 'Whether to emit OpenTelemetry spans for infrastructure calls.',
        'BILLING_PROVIDER_DEFAULT': 'Default gateway for new tenant subscriptions (stripe, mock).',
        'MASTER_SECRET': 'Critical key used for cross-tenant data signing and inter-service authentication.',
        'EMAIL_PROVIDER_DEFAULT': 'Primary provider for outbound emails (sendgrid, ses, console).',
        'SMS_PROVIDER_DEFAULT': 'Primary provider for outbound SMS (twilio, messagebird, mock).',
        'CACHE_ISOLATION_STRATEGY': 'Determines how cache data is separated (NAMESPACE vs CLUSTER).',
        'QUEUE_ISOLATION_STRATEGY': 'Determines how tasks are isolated (VHOST vs NAMESPACE).',
        'SEARCH_PROVIDER_DEFAULT': 'Primary provider for full-text search (elasticsearch, mock).',
    }

    # Settings that MUST be defined in settings.py (no defaults)
    REQUIRED = [
        'MASTER_SECRET', # Critical for inter-tenant signatures
    ]

    DEFAULTS = {
        'BASE_SAAS_DOMAIN': 'localhost',
        'MANAGED_APPS': ['tenants'],
        'STORAGE_PATH_PREFIX': 'tenants',
        'DEFAULT_ISOLATION': 'LOGICAL',
        'MIGRATION_PARALLELISM': 4,
        'QUOTA_STRICT_MODE': True,
        'BILLING_PROVIDER_DEFAULT': 'stripe',
        'AUDIT_LOG_RETENTION_DAYS': 90,
        'CIRCUIT_BREAKER_THRESHOLD': 5,
        'CIRCUIT_BREAKER_RESET_TIMEOUT': 60,
        'TRACING_ENABLED': True,
        'EMAIL_PROVIDER_DEFAULT': 'console',
        'SMS_PROVIDER_DEFAULT': 'mock',
        'WHATSAPP_PROVIDER_DEFAULT': 'mock',
        'CACHE_ISOLATION_STRATEGY': 'NAMESPACE',
        'QUEUE_ISOLATION_STRATEGY': 'NAMESPACE',
        'SEARCH_PROVIDER_DEFAULT': 'mock',
        'ELASTICSEARCH_URL': 'http://localhost:9200',
        'SANDBOX_MODE': False,
    }

    def __getattr__(self, name: str) -> Any:
        if name not in self.DEFAULTS and name not in self.REQUIRED:
            raise AttributeError(f"Setting '{name}' is not part of the Sovereign Engine.")
        
        val = getattr(settings, f"{self.PREFIX}{name}", self.DEFAULTS.get(name))
        
        if val is None and name in self.REQUIRED:
            from django.core.exceptions import ImproperlyConfigured
            raise ImproperlyConfigured(f"Sovereign Setting missing: {self.PREFIX}{name} is required for module operation.")
            
        return val

    def diagnose(self) -> dict:
        """
        Returns a detailed report of the configuration status per module.
        """
        report = {}
        for module, keys in self.MODULE_MAP.items():
            report[module] = []
            for key in keys:
                full_key = f"{self.PREFIX}{key}"
                has_override = hasattr(settings, full_key)
                value = getattr(settings, full_key, self.DEFAULTS.get(key))
                
                report[module].append({
                    "key": full_key,
                    "status": "CONFIGURED" if has_override else "DEFAULT",
                    "value": value if not isinstance(value, (dict, list)) else "[COMPLEX]",
                    "is_required": key in self.REQUIRED,
                    "description": self.METADATA.get(key, "No description provided.")
                })
        return report

    def validate_startup(self):
        """
        Tier 80: Fail-Fast Startup.
        Raises ImproperlyConfigured if any REQUIRED settings are missing.
        """
        missing = []
        for key in self.REQUIRED:
            full_key = f"{self.PREFIX}{key}"
            if not hasattr(settings, full_key):
                missing.append(full_key)
        
        if missing:
            from django.core.exceptions import ImproperlyConfigured
            raise ImproperlyConfigured(
                f"Sovereign Engine Startup Failed: Mandatory configuration missing: {', '.join(missing)}. "
                f"Please define these in your settings.py or .env file."
            )

from django.core.exceptions import ImproperlyConfigured
conf = SovereignConfig()
