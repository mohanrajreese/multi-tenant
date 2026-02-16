
from rest_framework import viewsets, permissions
from tenants.domain.models import TelemetryEntry
from tenants.api.serializers.serializers_base import TenantAwareSerializer
from rest_framework.response import Response
from rest_framework.decorators import action

class TelemetrySerializer(TenantAwareSerializer):
    class Meta:
        model = TelemetryEntry
        fields = ['id', 'provider', 'action', 'status', 'latency_ms', 'error_message', 'metadata', 'timestamp']

class TelemetryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Tier 94: Observability Consumption.
    Exposes infrastructure telemetry for the UI Dashboards.
    """
    queryset = TelemetryEntry.objects.all()
    serializer_class = TelemetrySerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def aggregate(self, request):
        """Returns aggregate metrics for the dashboard heatmap."""
        from django.db.models import Count, Avg
        stats = TelemetryEntry.objects.values('provider', 'status').annotate(
            count=Count('id'),
            avg_latency=Avg('latency_ms')
        )
        return Response(stats)
