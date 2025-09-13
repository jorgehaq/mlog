from typing import Optional

from fastapi import FastAPI
from loguru import logger

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter as OTLPSpanExporterGrpc
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter as OTLPSpanExporterHttp
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.core.config import settings


def init_tracing(app: FastAPI) -> Optional[str]:
    endpoint = getattr(settings, "OTEL_EXPORTER_OTLP_ENDPOINT", None)
    if not endpoint:
        return None
    try:
        resource = Resource(attributes={SERVICE_NAME: settings.APP_NAME})
        provider = TracerProvider(resource=resource)
        if endpoint.startswith("http"):
            exporter = OTLPSpanExporterHttp(endpoint=endpoint)
        else:
            exporter = OTLPSpanExporterGrpc(endpoint=endpoint)
        processor = BatchSpanProcessor(exporter)
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
        FastAPIInstrumentor.instrument_app(app)
        logger.info("OpenTelemetry tracing initialized")
        return endpoint
    except Exception as e:  # pragma: no cover
        logger.warning("OpenTelemetry init failed: {}", e)
        return None

