
import base64
import hashlib
from django.conf import settings
from cryptography.fernet import Fernet
from django.core.exceptions import ImproperlyConfigured

class SovereignVault:
    """
    Tier 91: Encrypted Secret Sovereignty.
    Provides AES-128 encryption for sensitive infrastructure secrets.
    Uses Fernet (Symmetric Encryption) derived from the platform's Master Secret.
    """
    _fernet = None

    @classmethod
    def _get_fernet(cls):
        if cls._fernet is None:
            # Derive a 32-byte key from the TENANT_MASTER_SECRET
            master_secret = getattr(settings, 'TENANT_MASTER_SECRET', None)
            if not master_secret or master_secret == 'sovereign-dev-secret-change-in-production':
                if not settings.DEBUG:
                    raise ImproperlyConfigured("TENANT_MASTER_SECRET must be set and secured for production encryption.")
            
            # Use SHA256 to derive a fixed-length key, then base64 encode for Fernet
            key_hash = hashlib.sha256(master_secret.encode()).digest()
            fernet_key = base64.urlsafe_b64encode(key_hash)
            cls._fernet = Fernet(fernet_key)
        return cls._fernet

    @classmethod
    def encrypt(cls, plaintext: str) -> str:
        """Encrypts a string and returns a base64 encoded ciphertext."""
        if not plaintext:
            return ""
        return cls._get_fernet().encrypt(plaintext.encode()).decode()

    @classmethod
    def decrypt(cls, ciphertext: str) -> str:
        """Decrypts a base64 encoded ciphertext and returns the plaintext."""
        if not ciphertext:
            return ""
        try:
            return cls._get_fernet().decrypt(ciphertext.encode()).decode()
        except Exception as e:
            # In a real system, log this securely without revealing the ciphertext
            return f"[DECRYPTION_FAILED]"

    @classmethod
    def protect_config(cls, config_dict: dict, sensitive_keys: list):
        """
        Helper to scan a config dict and encrypt specific sensitive fields.
        Useful for preprocessing before saving to Tenant.config.
        """
        protected = config_dict.copy()
        for key in sensitive_keys:
            if key in protected and protected[key] and not str(protected[key]).startswith('gAAAAA'): # Fernet prefix
                protected[key] = cls.encrypt(str(protected[key]))
        return protected

    @classmethod
    def unprotect_config(cls, config_dict: dict, sensitive_keys: list):
        """
        Helper to scan a config dict and decrypt specific sensitive fields.
        Useful for postprocessing after loading from Tenant.config.
        """
        unprotected = config_dict.copy()
        for key in sensitive_keys:
            if key in unprotected and str(unprotected[key]).startswith('gAAAAA'):
                unprotected[key] = cls.decrypt(str(unprotected[key]))
        return unprotected
