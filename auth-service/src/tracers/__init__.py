from core.config import trace_settings
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (BatchSpanProcessor,
                                            ConsoleSpanExporter)


def configure_tracer() -> None:
    resource = Resource(attributes={SERVICE_NAME: trace_settings.SERVICE_NAME})
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name=trace_settings.HOST,
                agent_port=trace_settings.PORT,
            )
        )
    )
    if trace_settings.TO_CONSOLE:
        # Чтобы видеть трейсы в консоли
        trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
