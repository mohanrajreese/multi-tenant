from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from tenants.infrastructure.hub import InfrastructureHub
from .api_base import TenantAwareViewSet
import logging

logger = logging.getLogger(__name__)

class CommunicationViewSet(viewsets.ViewSet):
    """
    Tier 78: Sovereign Communication API.
    Exposes unified messaging channels (Email, SMS, WhatsApp).
    Protected by Tenant Resolution & Sovereign Resilience.
    """
    
    def get_tenant(self, request):
        return getattr(request, 'tenant', None)

    @action(detail=False, methods=['post'])
    def email(self, request):
        """Send an email via the tenant's sovereign provider."""
        tenant = self.get_tenant(request)
        if not tenant:
            return Response({"error": "Tenant context required"}, status=status.HTTP_400_BAD_REQUEST)
        
        recipient = request.data.get('recipient')
        subject = request.data.get('subject')
        body = request.data.get('body')
        
        if not all([recipient, subject, body]):
            return Response({"error": "recipient, subject, and body are required"}, status=status.HTTP_400_BAD_REQUEST)
            
        provider = InfrastructureHub.email(tenant)
        success = provider.send_email(recipient, subject, body)
        
        if success:
            return Response({"status": "Email dispatched"}, status=status.HTTP_202_ACCEPTED)
        return Response({"error": "Failed to dispatch email"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def sms(self, request):
        """Send an SMS via the tenant's sovereign provider."""
        tenant = self.get_tenant(request)
        if not tenant:
            return Response({"error": "Tenant context required"}, status=status.HTTP_400_BAD_REQUEST)
            
        recipient = request.data.get('recipient')
        message = request.data.get('message')
        
        if not all([recipient, message]):
            return Response({"error": "recipient and message are required"}, status=status.HTTP_400_BAD_REQUEST)
            
        provider = InfrastructureHub.sms(tenant)
        success = provider.send_sms(recipient, message)
        
        if success:
            return Response({"status": "SMS dispatched"}, status=status.HTTP_202_ACCEPTED)
        return Response({"error": "Failed to dispatch SMS"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def whatsapp(self, request):
        """Send a WhatsApp message via the tenant's sovereign provider."""
        tenant = self.get_tenant(request)
        if not tenant:
            return Response({"error": "Tenant context required"}, status=status.HTTP_400_BAD_REQUEST)
            
        recipient = request.data.get('recipient')
        message = request.data.get('message')
        media_url = request.data.get('media_url')
        
        if not all([recipient, message]):
            return Response({"error": "recipient and message are required"}, status=status.HTTP_400_BAD_REQUEST)
            
        provider = InfrastructureHub.whatsapp(tenant)
        success = provider.send_whatsapp(recipient, message, media_url=media_url)
        
        if success:
            return Response({"status": "WhatsApp message dispatched"}, status=status.HTTP_202_ACCEPTED)
        return Response({"error": "Failed to dispatch WhatsApp message"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
