
from tenants.domain.models import Invoice
from django.conf import settings
from tenants.infrastructure.storage.factory import StorageFactory
import logging
from uuid import uuid4

logger = logging.getLogger(__name__)

class InvoiceService:
    """
    Tier 99: Sovereign Billing Engine.
    Handles invoice generation and payment execution.
    """
    
    @staticmethod
    def generate_pdf(invoice: Invoice):
        """
        Generates a PDF invoice and uploads it to tenant storage.
        """
        # industrial_invoice_template.html (Mock)
        content = f"""
        INVOICE #{invoice.invoice_number}
        --------------------------------
        Tenant: {invoice.tenant.name}
        Date: {invoice.created_at}
        Due: {invoice.due_date}
        
        Line Items:
        """
        for item in invoice.line_items:
            content += f"\n- {item.get('description')}: ${item.get('amount')}"
            
        content += f"\n\nTOTAL: {invoice.currency} {invoice.amount}"
        
        # Save to storage (Mock PDF as .txt for portability without ReportLab)
        filename = f"invoices/{invoice.invoice_number}.txt"
        storage = StorageFactory.get_storage(invoice.tenant)
        storage.save(filename, content.encode('utf-8'))
        
        # Update URL
        # In real S3, this would be a signed URL
        invoice.pdf_url = f"https://{settings.TENANT_BASE_SAAS_DOMAIN}/storage/{filename}"
        invoice.save()
        
        return invoice.pdf_url

    @staticmethod
    def execute_charge(invoice: Invoice):
        """
        Executes a charge against the tenant's payment method (Stripe).
        """
        if invoice.status == 'PAID':
            return True
            
        logger.info(f"[BILLING] Charging {invoice.amount} {invoice.currency} to {invoice.tenant.name} (Stripe Mock)")
        
        # Mock Stripe API Call
        import time
        time.sleep(0.5) # Simulate latency
        
        # Success path
        invoice.stripe_charge_id = f"ch_{uuid4()}"
        invoice.status = 'PAID'
        invoice.paid_at = settings.timezone.now() if hasattr(settings, 'timezone') else None
        invoice.save()
        
        return True
