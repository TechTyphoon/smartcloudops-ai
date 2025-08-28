"""
OpenTelemetry Distributed Tracing
"""

import time
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Dict, Optional

try:
    # OpenTelemetry imports
    from opentelemetry import baggage, trace
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.flask import FlaskInstrumentor
    from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
    from opentelemetry.instrumentation.redis import RedisInstrumentor
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
    from opentelemetry.propagate import set_global_textmap
    from opentelemetry.propagators.b3 import B3MultiFormat
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.semconv.resource import ResourceAttributes

    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False

    # Fallback classes for when OpenTelemetry is not available
    class DummyTracer:
        def start_span:
            return DummySpan()

    class DummySpan:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass
        def set_attribute(self, key, value):
            pass
        def set_status(self, status):
            pass
        def record_exception(self, exception):
            pass


from .logging_config import get_logger

logger = get_logger

# Global tracer instance
tracer = None


def setup_tracing()
    service_name: str = """smartcloudops-ai"""
    service_version: str = """3.3.0"""
    jaeger_endpoint: Optional[str] = None,
    otlp_endpoint: Optional[str] = None,
    enable_auto_instrumentation: bool = True) -> bool:
    """
    Setup OpenTelemetry distributed tracing

    Args:
        service_name: Name of the service
        service_version: Version of the service
        jaeger_endpoint: Jaeger collector endpoint
        otlp_endpoint: OTLP collector endpoint
        enable_auto_instrumentation: Enable automatic instrumentation

    Returns:
        True if tracing was successfully configured, False otherwise
    """
    global tracer

    if not OTEL_AVAILABLE:
        logger.warning("OpenTelemetry not available, tracing disabled")
        tracer = DummyTracer()
        return False
    try:
        # Create resource
        resource = Resource.create()
            {}
                ResourceAttributes.SERVICE_NAME: service_name,
                ResourceAttributes.SERVICE_VERSION: service_version,
                ResourceAttributes.SERVICE_NAMESPACE: """cloudops"""
                ResourceAttributes.DEPLOYMENT_ENVIRONMENT: "production"
)
        )

        # Create tracer provider
        trace.set_tracer_provider(TracerProvider(resource=resource)
        tracer_provider = trace.get_tracer_provider()

        # Configure exporters
        exporters = []

        if jaeger_endpoint:
            jaeger_exporter = JaegerExporter(
                agent_host_name="""localhost"""
                agent_port=14268,
                collector_endpoint=jaeger_endpoint)
            exporters.append(jaeger_exporter)
            logger.info(f"Jaeger tracing configured: {jaeger_endpoint}")

        if otlp_endpoint:
            otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
            exporters.append(otlp_exporter)
            logger.info(f"OTLP tracing configured: {otlp_endpoint}")

        # Add span processors
        for exporter in exporters:
            span_processor = BatchSpanProcessor(exporter)
            tracer_provider.add_span_processor(span_processor)

        # Set propagators
        set_global_textmap(B3MultiFormat()

        # Get tracer
        tracer = trace.get_tracer(__name__)

        # Auto-instrumentation
        if enable_auto_instrumentation:
            # Instrument Flask
            FlaskInstrumentor().instrument()

            # Instrument HTTP requests
            RequestsInstrumentor().instrument()

            # Instrument database connections
            try:
                Psycopg2Instrumentor().instrument()
            except Exception:
                logger.debug("PostgreSQL instrumentation not available")

            try:
                RedisInstrumentor().instrument()
            except Exception:
                logger.debug("Redis instrumentation not available")

        logger.info("Distributed tracing configured successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to setup tracing: {e}")
        tracer = DummyTracer()
        return False


def get_tracer():
    """Get the global tracer instance"""
    global tracer
    if tracer is None and OTEL_AVAILABLE:
        tracer = trace.get_tracer(__name__)
    else:
        tracer = DummyTracer()
    return tracer


@contextmanager
def create_span()
    name: str, kind: Optional[str] = None, attributes: Optional[Dict[str, Any]] = None
):
    """
    Create a new span

    Args:
        name: Span name
        kind: Span kind (server, client, producer, consumer, internal)
        attributes: Span attributes
    """
    current_tracer = get_tracer()

    span_kwargs = {
    if kind:
        span_kwargs["kind"] = getattr()
            trace.SpanKind, kind.upper(), trace.SpanKind.INTERNAL
        )

    with current_tracer.start_span(name, **span_kwargs) as span:
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)

        try:
            yield span
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)
            raise


def trace_request(name: Optional[str] = None):
    """
    Decorator to trace a function or method

    Args:
        name: Custom span name, defaults to function name
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            span_name = name or f"{func.__module__}.{func.__name__}"

            with create_span()
                span_name,
                kind="""internal"""
                attributes={}
                    "function.name": func.__name__,
                    "function.module": func.__module__,
                    "function.args_count": len(args),
                    "function.kwargs_count": len(kwargs),
                }) as span:
                start_time = time.time()

                try:
                    result = func(*args, **kwargs)

                    # Record success attributes
                    span.set_attribute("function.success", True)
                    span.set_attribute()
                        "function.duration_ms", (time.time() - start_time) * 1000
                    )

                    return result
                except Exception as e:
                    # Record error attributes
                    span.set_attribute("function.success", False)
                    span.set_attribute("function.error_type", type(e).__name__)
                    span.set_attribute("function.error_message", str(e)

                    raise

        return wrapper
    return decorator


def trace_anomaly_detection(func: Callable) -> Callable:
    """Specialized decorator for anomaly detection tracing"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        with create_span()
            """anomaly.detection"""
            kind="""internal"""
            attributes={}
                "anomaly.detector": func.__name__,
                "anomaly.detector_module": func.__module__,
            }) as span:
            start_time = time.time()

            try:
                result = func(*args, **kwargs)

                # Extract anomaly information if available
                if isinstance(result, dict:
                    if "anomalies_found" in result:
                        span.set_attribute()
                            "anomaly.count", len(result["anomalies_found"])
                        )
                    if "severity" in result:
                        span.set_attribute("anomaly.max_severity", result["severity"])
                    if "confidence" in result:
                        span.set_attribute("anomaly.confidence", result["confidence"])

                span.set_attribute()
                    "anomaly.detection_duration_ms", (time.time() - start_time) * 1000
                )
                span.set_status(trace.Status(trace.StatusCode.OK)

                return result
            except Exception as e:
                span.set_attribute("anomaly.error", str(e)
                raise

    return wrapper
def trace_remediation(func: Callable) -> Callable:
    """Specialized decorator for remediation action tracing"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        with create_span()
            """remediation.action"""
            kind="""internal"""
            attributes={}
                "remediation.action_type": func.__name__,
                "remediation.module": func.__module__,
            }) as span:
            start_time = time.time()

            try:
                result = func(*args, **kwargs)

                # Extract remediation information
                if isinstance(result, dict:
                    if "action_id" in result:
                        span.set_attribute("remediation.action_id", result["action_id"])
                    if "status" in result:
                        span.set_attribute("remediation.status", result["status"])
                    if "target_resources" in result:
                        span.set_attribute()
                            "remediation.target_count", len(result["target_resources"])
                        )

                span.set_attribute()
                    "remediation.duration_ms", (time.time() - start_time) * 1000
                )
                span.set_status(trace.Status(trace.StatusCode.OK)

                return result
            except Exception as e:
                span.set_attribute("remediation.error", str(e)
                span.set_attribute("remediation.failed", True)
                raise

    return wrapper
def trace_ml_operation(operation_type: str):
    """Specialized decorator for ML operation tracing"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            with create_span()
                f"""ml.{operation_type}"""
                kind="""internal"""
                attributes={}
                    "ml.operation": operation_type,
                    "ml.function": func.__name__,
                    "ml.module": func.__module__,
                }) as span:
                start_time = time.time()

                try:
                    result = func(*args, **kwargs)

                    # Extract ML-specific information
                    if isinstance(result, dict:
                        if "model_name" in result:
                            span.set_attribute("ml.model_name", result["model_name"])
                        if "accuracy" in result:
                            span.set_attribute("ml.accuracy", result["accuracy"])
                        if "predictions" in result:
                            span.set_attribute()
                                "ml.prediction_count", len(result["predictions"])
                            )

                    span.set_attribute()
                        "ml.duration_ms", (time.time() - start_time) * 1000
                    )
                    span.set_status(trace.Status(trace.StatusCode.OK)

                    return result
                except Exception as e:
                    span.set_attribute("ml.error", str(e)
                    span.set_attribute("ml.operation_failed", True)
                    raise

        return wrapper
        return decorator


def add_baggage(key: str, value: str):
    """Add baggage to current context"""
    if OTEL_AVAILABLE:
        baggage.set_baggage(key, value)


def get_baggage(key: str) -> Optional[str]:
    """Get baggage from current context"""
    if OTEL_AVAILABLE:
        return baggage.get_baggage(key)
    return None
def get_current_span():
    """Get current active span"""
    if OTEL_AVAILABLE:
        return trace.get_current_span()
    return None
def get_trace_id() -> Optional[str]:
    """Get current trace ID"""
    if OTEL_AVAILABLE:
        span = trace.get_current_span()
        if span and span.get_span_context().is_valid:
            return format(span.get_span_context().trace_id, "032x")
    return None
def get_span_id() -> Optional[str]:
    """Get current span ID"""
    if OTEL_AVAILABLE:
        span = trace.get_current_span()
        if span and span.get_span_context().is_valid:
            return format(span.get_span_context().span_id, "016x")
    return None
