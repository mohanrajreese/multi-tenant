import logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from django.conf import settings

logger = logging.getLogger(__name__)

def setup_telemetry():
    """
    Tier 71: Distributed Tracing Setup.
    Configures OpenTelemetry with OTLP and Console exporters.
    """
    try:
        resource = Resource(attributes={
            SERVICE_NAME: "sovereign-engine"
        })

        provider = TracerProvider(resource=resource)
        
        # 1. Console exporter (Visible in 'runserver' dev console)
        # Use SimpleSpanProcessor for more reliable stdout in some environments
        if settings.DEBUG:
            processor = SimpleSpanProcessor(ConsoleSpanExporter())
            provider.add_span_processor(processor)

        # 2. OTLP exporter (For Jaeger/Analytics)
        otlp_endpoint = getattr(settings, 'OTEL_EXPORTER_OTLP_ENDPOINT', None)
        if otlp_endpoint:
            otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
            provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

        trace.set_tracer_provider(provider)
        
        # 3. Automatic Django Instrumentation (Delayed import to prevent hang)
        # We skip automatic instrumentor if it causes hangs in specific environments
        # from opentelemetry.instrumentation.django import DjangoInstrumentor
        # DjangoInstrumentor().instrument()
        
        logger.info("[TELEMETRY] OpenTelemetry Tracing initialized (Manual Hub Spans).")
    except Exception as e:
        logger.warning(f"[TELEMETRY] Failed to initialize tracing: {e}")

def get_tracer():
    return trace.get_tracer("sovereign.engine")
