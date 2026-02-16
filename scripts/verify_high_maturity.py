
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Disable background offloading for verification
settings.TESTING = True

from tenants.infrastructure.security.vault import SovereignVault
from tenants.infrastructure.hub import InfrastructureHub
from tenants.domain.models import Tenant, TelemetryEntry

def verify_vault():
    print("\n🔐 Verifying Sovereign Vault (Tier 91)...")
    secret = "twilio-super-secret-token"
    encrypted = SovereignVault.encrypt(secret)
    decrypted = SovereignVault.decrypt(encrypted)
    
    print(f"  Plaintext: {secret}")
    print(f"  Encrypted: {encrypted[:20]}...")
    print(f"  Decrypted: {decrypted}")
    
    assert secret == decrypted
    print("  ✅ Vault Integrity Verified.")

def verify_telemetry():
    print("\n📊 Verifying Telemetry Bridge (Tier 94)...")
    tenant = Tenant.objects.first()
    if not tenant:
        print("  ⚠️ No tenant found for testing. Skipping.")
        return

    # Simulate a call through the hub
    # We'll use the sandbox mode to trigger a succession
    from tenants.infrastructure.conf import conf
    conf.SANDBOX_MODE = False # Force real path to trigger proxy
    
    email_provider = InfrastructureHub.email(tenant)
    print(f"  Provider type: {type(email_provider)}")
    
    # Trigger a mock call through the proxy
    email_provider.send_email("test@example.com", "Subject", "Body")
    
    # Check TelemetryEntry
    entry = TelemetryEntry.objects.filter(tenant=tenant, provider="EMAIL").first()
    if entry:
        print(f"  ✅ Telemetry Captured: {entry.provider} - {entry.action} ({entry.status})")
        print(f"  Latency: {entry.latency_ms}ms")
    else:
        print("  ❌ Telemetry Recording Failed.")

if __name__ == "__main__":
    verify_vault()
    verify_telemetry()
