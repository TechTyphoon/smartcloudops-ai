"""
Enhanced OpenTelemetry Configuration
Phase 4: Observability & Operability - Distributed tracing and metrics
"""

import os
from typing import Optional

from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
# from opentelemetry.instrumentation.logging import LoggingInstrumentor  # Not available in current version
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
from opentelemetry.sdk.resources import Resource
# from opentelemetry.propagator.b3 import B3Format  # Not available in current version
from opentelemetry.propagate import set_global_textmap


class OpenTelemetryConfig:
    """OpenTelemetry configuration manager"""

    def __init__(self):
        self.tracer_provider: Optional[TracerProvider] = None
        self.meter_provider: Optional[MeterProvider] = None
        self.tracer = None
        self.meter = None
        self._configured = False

    def setup(
        self,
        service_name: str = "smartcloudops-ai",
        service_version: str = "4.0.0",
        environment: str = "development",
        enable_tracing: bool = True,
        enable_metrics: bool = True,
        enable_logging_instrumentation: bool = True,
        jaeger_endpoint: Optional[str] = None,
        otlp_endpoint: Optional[str] = None,
        console_export: bool = False,
    ) -> None:
        """
        Setup OpenTelemetry with tracing and metrics

        Args:
            service_name: Name of the service
            service_version: Version of the service
            environment: Environment (development, staging, production)
            enable_tracing: Enable distributed tracing
            enable_metrics: Enable metrics collection
            enable_logging_instrumentation: Enable logging instrumentation
            jaeger_endpoint: Jaeger collector endpoint
            otlp_endpoint: OTLP collector endpoint
            console_export: Enable console export for debugging
        """
        if self._configured:
            return

        # Create resource with service information
        resource = Resource.create({
            "service.name": service_name,
            "service.version": service_version,
            "service.namespace": "smartcloudops",
            "deployment.environment": environment,
            "host.name": os.getenv("HOSTNAME", "unknown"),
            "process.pid": str(os.getpid()),
        })

        # Setup tracing
        if enable_tracing:
            self._setup_tracing(resource, jaeger_endpoint, otlp_endpoint, console_export)

        # Setup metrics
        if enable_metrics:
            self._setup_metrics(resource, otlp_endpoint, console_export)

        # Setup logging instrumentation
        if enable_logging_instrumentation:
            self._setup_logging_instrumentation()

        # Setup propagators
        self._setup_propagators()

        self._configured = True

    def _setup_tracing(
        self,
        resource: Resource,
        jaeger_endpoint: Optional[str],
        otlp_endpoint: Optional[str],
        console_export: bool,
    ) -> None:
        """Setup distributed tracing"""
        # Create tracer provider
        self.tracer_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(self.tracer_provider)

        # Add span processors
        processors = []

        # Console exporter for debugging
        if console_export:
            console_processor = BatchSpanProcessor(ConsoleSpanExporter())
            processors.append(console_processor)

        # Jaeger exporter
        if jaeger_endpoint:
            jaeger_exporter = JaegerExporter(
                agent_host_name=jaeger_endpoint.split(":")[0],
                agent_port=int(jaeger_endpoint.split(":")[1]) if ":" in jaeger_endpoint else 6831,
            )
            jaeger_processor = BatchSpanProcessor(jaeger_exporter)
            processors.append(jaeger_processor)

        # OTLP exporter
        if otlp_endpoint:
            otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
            otlp_processor = BatchSpanProcessor(otlp_exporter)
            processors.append(otlp_processor)

        # Add processors to provider
        for processor in processors:
            self.tracer_provider.add_span_processor(processor)

        # Create tracer
        self.tracer = trace.get_tracer(__name__)

    def _setup_metrics(
        self,
        resource: Resource,
        otlp_endpoint: Optional[str],
        console_export: bool,
    ) -> None:
        """Setup metrics collection"""
        # Create meter provider
        readers = []

        # Console exporter for debugging
        if console_export:
            console_reader = PeriodicExportingMetricReader(
                ConsoleMetricExporter(),
                export_interval_millis=5000,
            )
            readers.append(console_reader)

        # OTLP exporter
        if otlp_endpoint:
            otlp_exporter = OTLPMetricExporter(endpoint=otlp_endpoint)
            otlp_reader = PeriodicExportingMetricReader(
                otlp_exporter,
                export_interval_millis=10000,
            )
            readers.append(otlp_reader)

        if readers:
            self.meter_provider = MeterProvider(resource=resource, metric_readers=readers)
            metrics.set_meter_provider(self.meter_provider)
            self.meter = metrics.get_meter(__name__)

    def _setup_logging_instrumentation(self) -> None:
        """Setup logging instrumentation"""
        # LoggingInstrumentor not available in current version
        # LoggingInstrumentor().instrument(
        #     set_logging_format=True,
        #     log_level=os.getenv("LOG_LEVEL", "INFO"),
        # )
        pass

    def _setup_propagators(self) -> None:
        """Setup context propagators"""
        # B3 propagator not available in current version
        # b3_propagator = B3Format()
        # set_global_textmap(b3_propagator)
        pass

    def instrument_flask(self, app) -> None:
        """Instrument Flask application"""
        if not self._configured:
            raise RuntimeError("OpenTelemetry not configured. Call setup() first.")

        FlaskInstrumentor().instrument_app(app)

    def instrument_requests(self) -> None:
        """Instrument requests library"""
        if not self._configured:
            raise RuntimeError("OpenTelemetry not configured. Call setup() first.")

        RequestsInstrumentor().instrument()

    def instrument_psycopg2(self) -> None:
        """Instrument PostgreSQL connections"""
        if not self._configured:
            raise RuntimeError("OpenTelemetry not configured. Call setup() first.")

        Psycopg2Instrumentor().instrument()

    def instrument_redis(self) -> None:
        """Instrument Redis connections"""
        if not self._configured:
            raise RuntimeError("OpenTelemetry not configured. Call setup() first.")

        RedisInstrumentor().instrument()

    def get_tracer(self, name: str = None):
        """Get tracer instance"""
        if not self._configured:
            raise RuntimeError("OpenTelemetry not configured. Call setup() first.")

        return trace.get_tracer(name or __name__)

    def get_meter(self, name: str = None):
        """Get meter instance"""
        if not self._configured:
            raise RuntimeError("OpenTelemetry not configured. Call setup() first.")

        return metrics.get_meter(name or __name__)

    def shutdown(self) -> None:
        """Shutdown OpenTelemetry"""
        if self.tracer_provider:
            self.tracer_provider.shutdown()
        if self.meter_provider:
            self.meter_provider.shutdown()


# Global OpenTelemetry configuration instance
otel_config = OpenTelemetryConfig()


def setup_opentelemetry(
    app=None,
    service_name: str = "smartcloudops-ai",
    service_version: str = "4.0.0",
    environment: str = None,
    **kwargs,
) -> OpenTelemetryConfig:
    """
    Setup OpenTelemetry for the application

    Args:
        app: Flask application instance
        service_name: Name of the service
        service_version: Version of the service
        environment: Environment (defaults to FLASK_ENV)
        **kwargs: Additional configuration options

    Returns:
        OpenTelemetryConfig instance
    """
    if environment is None:
        environment = os.getenv("FLASK_ENV", "development")

    # Get endpoints from environment
    jaeger_endpoint = os.getenv("JAEGER_ENDPOINT")
    otlp_endpoint = os.getenv("OTLP_ENDPOINT")
    console_export = os.getenv("OTEL_CONSOLE_EXPORT", "false").lower() == "true"

    # Setup OpenTelemetry
    otel_config.setup(
        service_name=service_name,
        service_version=service_version,
        environment=environment,
        jaeger_endpoint=jaeger_endpoint,
        otlp_endpoint=otlp_endpoint,
        console_export=console_export,
        **kwargs,
    )

    # Instrument Flask if provided
    if app:
        otel_config.instrument_flask(app)

    # Instrument other libraries
    otel_config.instrument_requests()
    otel_config.instrument_psycopg2()
    otel_config.instrument_redis()

    return otel_config


def get_tracer(name: str = None):
    """Get OpenTelemetry tracer"""
    return otel_config.get_tracer(name)


def get_meter(name: str = None):
    """Get OpenTelemetry meter"""
    return otel_config.get_meter(name)


def create_span(name: str, **attributes):
    """Create a span with attributes"""
    tracer = get_tracer()
    with tracer.start_as_current_span(name) as span:
        for key, value in attributes.items():
            if isinstance(value, (str, int, float, bool)):
                span.set_attribute(key, value)
        return span


def trace_function(name: str = None):
    """Decorator to trace function execution"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            tracer = get_tracer()
            span_name = name or f"{func.__module__}.{func.__name__}"
            
            with tracer.start_as_current_span(span_name) as span:
                # Add function attributes
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)
                
                try:
                    result = func(*args, **kwargs)
                    span.set_status(trace.Status(trace.StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise
        return wrapper
    return decorator
