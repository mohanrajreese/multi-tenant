from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from tenants.infrastructure.hub import InfrastructureHub
from tenants.infrastructure.utils.context import get_current_tenant
from tenants.api.serializers.serializers_intelligence import IntelligencePromptSerializer, IntelligenceResponseSerializer

class IntelligenceViewSet(viewsets.ViewSet):
    """
    Tier 65: Sovereign Intelligence Interface.
    Exposes the configured AI Provider (OpenAI/Anthropic/Ollama) to the frontend.
    """
    
    @extend_schema(
        request=IntelligencePromptSerializer,
        responses={200: IntelligenceResponseSerializer},
        summary="Ask the Tenant's AI",
        description="Generates text using the tenant's configured LLM provider."
    )
    @action(detail=False, methods=['post'], url_path='ask')
    def ask(self, request):
        serializer = IntelligencePromptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        prompt = serializer.validated_data['prompt']
        system_prompt = serializer.validated_data.get('system_prompt')
        
        tenant = get_current_tenant()
        provider = InfrastructureHub.intelligence(tenant)
        
        # Execute Generation
        response_text = provider.generate_text(prompt, system_prompt=system_prompt)
        
        return Response({
            'response': response_text,
            'model_used': getattr(provider, 'model', 'unknown')
        })
