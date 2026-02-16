
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Disable background offloading for verification
settings.TESTING = True

from tenants.domain.models import Tenant, Quota, Invoice
from tenants.business.use_cases.core.services_quota import QuotaService
from tenants.business.use_cases.billing.services_billing import InvoiceService
from tenants.tasks import cleanup_expired_data
from tenants.infrastructure.control.services_offboarding import OffboardingService

def verify_hierarchy():
    print("\n🌳 Verifying Organizational Hierarchy (Tier 98)...")
    # 1. Create Parent
    parent = Tenant.objects.create(name="Holding Corp", slug="holding-corp")
    print(f"  Parent: {parent.name}")
    
    # 2. Create Child
    child = Tenant.objects.create(name="Subsidiary A", slug="sub-a", parent=parent)
    print(f"  Child: {child.name} (Parent: {child.parent.name})")
    
    # 3. Verify Ancestors
    ancestors = child.get_ancestors()
    print(f"  Ancestors: {[t.name for t in ancestors]}")
    assert len(ancestors) == 2
    assert ancestors[1].slug == 'holding-corp'
    print("  ✅ Hierarchy Traversal Verified.")
    
    # 4. Verify Recursive Quota
    print("  Testing Recursive Quota...")
    Quota.objects.create(tenant=parent, resource_name="users", limit_value=5, current_usage=0)
    
    # Increment child usage
    QuotaService.increment_usage(child, "users", 3)
    
    # Check Parent Usage
    parent_quota = Quota.objects.get(tenant=parent, resource_name="users")
    print(f"  Parent Usage after Child increment: {parent_quota.current_usage}")
    assert parent_quota.current_usage == 3
    
    # Try to exceed parent limit via child
    try:
        QuotaService.check_quota(child, "users", 3) # 3+3 = 6 > 5
        print("  ❌ Failed to block quota overflow.")
    except Exception as e:
        print(f"  ✅ Quota Blocked Correctly: {e}")

    return child

def verify_billing(tenant):
    print("\n💸 Verifying Sovereign Billing (Tier 99)...")
    invoice = Invoice.objects.create(
        tenant=tenant,
        invoice_number="INV-001",
        amount=500.00,
        currency="USD",
        status="DRAFT",
        line_items=[{"description": "SaaS Subscription", "amount": 500.00}]
    )
    
    # 1. Generate PDF
    url = InvoiceService.generate_pdf(invoice)
    print(f"  PDF Generated: {url}")
    
    # 2. Charge
    success = InvoiceService.execute_charge(invoice)
    print(f"  Charge Executed: {success} (Status: {invoice.status})")
    assert invoice.status == 'PAID'
    print("  ✅ Billing Cycle Verified.")

def verify_compliance(tenant):
    print("\n⚖️ Verifying Compliance & Operations (Tier 100)...")
    
    # 1. Retention
    result = cleanup_expired_data(tenant_id=tenant.id)
    print(f"  Retention Task: {result}")
    
    # 2. Secure Wipe
    # Note: We won't actually delete the tenant effectively here as unrelated tests might need it,
    # but we will call the logic on a temporary dummy tenant.
    dummy = Tenant.objects.create(name="To Delete", slug="delete-me", isolation_mode='LOGICAL')
    OffboardingService.purge_tenant(dummy)
    
    try:
        Tenant.objects.get(id=dummy.id)
        print("  ❌ Tenant still exists after purge.")
    except Tenant.DoesNotExist:
        print("  ✅ Tenant Securely Wiped.")

if __name__ == "__main__":
    child_tenant = verify_hierarchy()
    verify_billing(child_tenant)
    verify_compliance(child_tenant)
