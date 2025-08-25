#!/usr/bin/env python3
"""
GOD MODE: Centralized Logging System with ELK Stack Integration
Enterprise-grade logging with structured data, real-time processing,
and advanced analytics
"""

import logging
import os
import threading

# Elasticsearch integration
try:
    ELASTICSEARCH_AVAILABLE = True
except ImportError:
    ELASTICSEARCH_AVAILABLE = False

# OpenTelemetry for distributed tracing
try:
    # from opentelemetry.instrumentation.flask import FlaskInstrumentor
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class LogEntry:
    """Structured log entry with metadata"""

    timestamp: datetime
    level: str
    message: str
    service: str
    component: str
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    status_code: Optional[int] = None
    response_time_ms: Optional[float] = None
    error_details: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    severity_score: Optional[int] = None


@dataclass
class LogMetrics:
    """Log analytics metrics"""

    total_logs: int
    error_count: int
    warning_count: int
    info_count: int
    debug_count: int
    avg_response_time: float
    error_rate: float
    top_endpoints: List[Dict[str, Any]]
    top_errors: List[Dict[str, Any]]
    performance_trends: List[Dict[str, Any]]


class CentralizedLoggingSystem:
    """
    Enterprise-grade centralized logging system with ELK integration
    """

    def __init__(
        self,
        service_name: str = "smartcloudops-ai",
        elasticsearch_url: str = "http://elasticsearch:9200",
        log_file_path: str = "logs/centralized.logf",
        max_queue_size: int = 10000,
        batch_size: int = 100,
        flush_interval: int = 5,
    ):

        self.service_name = service_name
        self.log_file_path = log_file_path
        self.max_queue_size = max_queue_size
        self.batch_size = batch_size
        self.flush_interval = flush_interval

        # Initialize components
        self.log_queue = Queue(maxsize=max_queue_size)
        self.metrics = LogMetrics(
            total_logs=0,
            error_count=0,
            warning_count=0,
            info_count=0,
            debug_count=0,
            avg_response_time=0.0,
            error_rate=0.0,
            top_endpoints=[],
            top_errors=[],
            performance_trends=[],
        )

        # Performance tracking
        self.endpoint_stats = {}
        self.error_stats = {}
        self.response_times = []

        # Threading
        self.running = False
        self.worker_thread = None
        self.metrics_thread = None
        self.lock = threading.Lock()

        # Initialize Elasticsearch
        self.elasticsearch = None
        if ELASTICSEARCH_AVAILABLE:
            try:
                self.elasticsearch = Elasticsearch([elasticsearch_url])
                if self.elasticsearch.ping():
                    logger.info("✅ Elasticsearch connected successfully")
                else:
                    logger.warning("⚠️ Elasticsearch connection failed")
                    self.elasticsearch = None
            except Exception as e:
                logger.warning(f"⚠️ Elasticsearch not available: {e}")
                self.elasticsearch = None

        # Initialize OpenTelemetry
        if OPENTELEMETRY_AVAILABLE:
            self._setup_opentelemetry()

        # Create log directory
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

        # Start background workers
        self.start()

        logger.info(f"Centralized logging system initialized for {service_name}")

    def _setup_opentelemetry(self):
        """Setup OpenTelemetry for distributed tracing"""
        try:
            # Create tracer provider
            trace.set_tracer_provider(TracerProvider())
            # tracer = trace.get_tracer(__name__)

            # Setup Jaeger exporter
            jaeger_exporter = JaegerExporter(
                agent_host_name="jaeger",
                agent_port=6831,
            )

            # Add batch processor
            trace.get_tracer_provider().add_span_processor(
                BatchSpanProcessor(jaeger_exporter)
            )

            logger.info("✅ OpenTelemetry tracing initialized")

        except Exception as e:
            logger.warning(f"⚠️ OpenTelemetry setup failed: {e}")

    def start(self):
        """Start background workers"""
        if self.running:
            return

        self.running = True

        # Start log processor worker
        self.worker_thread = threading.Thread(target=self._log_worker, daemon=True)
        self.worker_thread.start()

        # Start metrics worker
        self.metrics_thread = threading.Thread(target=self._metrics_worker, daemon=True)
        self.metrics_thread.start()

        logger.info("Centralized logging workers started")

    def stop(self):
        """Stop background workers"""
        self.running = False

        if self.worker_thread:
            self.worker_thread.join(timeout=5)

        if self.metrics_thread:
            self.metrics_thread.join(timeout=5)

        # Flush remaining logs
        self._flush_logs()

        logger.info("Centralized logging workers stopped")

    def log(
        self, level: str, message: str, component: str = "general", **kwargs
    ) -> None:
        """Log a structured message"""

        # Create log entry
        log_entry = LogEntry(
            timestamp=datetime.now(),
            level=level.upper(),
            message=message,
            service=self.service_name,
            component=component,
            trace_id=kwargs.get("trace_id"),
            span_id=kwargs.get("span_id"),
            user_id=kwargs.get("user_id"),
            session_id=kwargs.get("session_id"),
            request_id=kwargs.get("request_id"),
            ip_address=kwargs.get("ip_address"),
            user_agent=kwargs.get("user_agent"),
            endpoint=kwargs.get("endpoint"),
            method=kwargs.get("method"),
            status_code=kwargs.get("status_code"),
            response_time_ms=kwargs.get("response_time_ms"),
            error_details=kwargs.get("error_details"),
            context=kwargs.get("context"),
            tags=kwargs.get("tags", []),
            severity_score=self._calculate_severity_score(level, kwargs),
        )

        # Add to queue
        try:
            self.log_queue.put_nowait(log_entry)
        except Exception:
            # Queue full, log to stderr as fallback
            print(f"LOG QUEUE FULL: {log_entry}", file=sys.stderr)

    def _calculate_severity_score(self, level: str, kwargs: Dict[str, Any]) -> int:
        """Calculate severity score for log entry""f"
        base_scores = {"DEBUG": 1, "INFO": 2, "WARNING": 3, "ERROR": 4, "CRITICAL": 5}

        score = base_scores.get(level.upper(), 2)

        # Adjust based on context
        if kwargs.get("status_code") and kwargs["status_code"] >= 500:
            score += 2
        elif kwargs.get("status_code") and kwargs["status_code"] >= 400:
            score += 1

        if kwargs.get("error_details"):
            score += 1

        if kwargs.get("response_time_ms", 0) > 1000:  # Slow response
            score += 1

        return min(score, 10)  # Cap at 10

    def _log_worker(self):
        """Background worker for processing logs"""
        batch = []
        last_flush = time.time()

        while self.running:
            try:
                # Get log entry with timeout
                log_entry = self.log_queue.get(timeout=1)
                batch.append(log_entry)

                # Update metrics
                self._update_metrics(log_entry)

                # Flush if batch is full or time has passed
                current_time = time.time()
                if (
                    len(batch) >= self.batch_size
                    or current_time - last_flush >= self.flush_interval
                ):

                    self._flush_batch(batch)
                    batch = []
                    last_flush = current_time

            except Empty:
                # Timeout, flush any remaining logs
                if batch:
                    self._flush_batch(batch)
                    batch = []
                    last_flush = time.time()
            except Exception as e:
                logger.error(f"Error in log worker: {e}")

    def _flush_batch(self, batch: List[LogEntry]):
        """Flush a batch of log entries"""
        if not batch:
            return

        # Write to file
        self._write_to_file(batch)

        # Send to Elasticsearch
        if self.elasticsearch:
            self._send_to_elasticsearch(batch)

        # Update performance stats
        self._update_performance_stats(batch)

    def _write_to_file(self, batch: List[LogEntry]):
        """Write log batch to file"""
        try:
            with open(self.log_file_path, "a", encoding="utf-8") as f:
                for entry in batch:
                    log_line = self._format_log_line(entry)
                    f.write(log_line + "\n")
        except Exception as e:
            print(f"Error writing to log file: {e}", file=sys.stderr)

    def _format_log_line(self, entry: LogEntry) -> str:
        """Format log entry as JSON line"""
        log_data = asdict(entry)
        log_data["timestamp"] = entry.timestamp.isoformat()
        return json.dumps(log_data, ensure_ascii=False)

    def _send_to_elasticsearch(self, batch: List[LogEntry]):
        """Send log batch to Elasticsearch"""
        try:
            # Prepare documents for bulk indexing
            actions = []
            for entry in batch:
                doc = asdict(entry)
                doc["timestamp"] = entry.timestamp.isoformat()
                doc["@timestampf"] = entry.timestamp.isoformat()

                action = {
                    "_index": f'logs-{entry.timestamp.strftime("%Y.%m.%d")}',
                    "_source": doc,
                }
                actions.append(action)

            # Bulk index
            if actions:
                helpers.bulk(self.elasticsearch, actions)

        except Exception as e:
            logger.error(f"Error sending to Elasticsearch: {e}")

    def _update_metrics(self, entry: LogEntry):
        """Update metrics with log entry"""
        with self.lock:
            self.metrics.total_logs += 1

            if entry.level == "ERROR":
                self.metrics.error_count += 1
            elif entry.level == "WARNING":
                self.metrics.warning_count += 1
            elif entry.level == "INFO":
                self.metrics.info_count += 1
            elif entry.level == "DEBUG":
                self.metrics.debug_count += 1

            # Update response time
            if entry.response_time_ms:
                self.response_times.append(entry.response_time_ms)
                if len(self.response_times) > 1000:  # Keep last 1000
                    self.response_times = self.response_times[-1000:]

                self.metrics.avg_response_time = sum(self.response_times) / len(
                    self.response_times
                )

            # Update error rate
            if self.metrics.total_logs > 0:
                self.metrics.error_rate = (
                    self.metrics.error_count / self.metrics.total_logs
                )

    def _update_performance_stats(self, batch: List[LogEntry]):
        """Update performance statistics""f"
        with self.lock:
            for entry in batch:
                # Endpoint stats
                if entry.endpoint:
                    if entry.endpoint not in self.endpoint_stats:
                        self.endpoint_stats[entry.endpoint] = {
                            "count": 0,
                            "errors": 0,
                            "avg_response_time": 0,
                        }

                    self.endpoint_stats[entry.endpoint]["count"] += 1
                    if entry.status_code and entry.status_code >= 400:
                        self.endpoint_stats[entry.endpoint]["errors"] += 1

                    if entry.response_time_ms:
                        current_avg = self.endpoint_stats[entry.endpoint][
                            "avg_response_time"
                        ]
                        count = self.endpoint_stats[entry.endpoint]["count"]
                        new_avg = (
                            current_avg * (count - 1) + entry.response_time_ms
                        ) / count
                        self.endpoint_stats[entry.endpoint][
                            "avg_response_time"
                        ] = new_avg

                # Error stats
                if entry.level == "ERROR" and entry.error_details:
                    error_type = entry.error_details.get("type", "unknown")
                    if error_type not in self.error_stats:
                        self.error_stats[error_type] = 0
                    self.error_stats[error_type] += 1

    def _metrics_worker(self):
        """Background worker for updating metrics"""
        while self.running:
            try:
                time.sleep(60)  # Update every minute
                self._update_metrics_summary()
            except Exception as e:
                logger.error(f"Error in metrics worker: {e}")

    def _update_metrics_summary(self):
        """Update metrics summary""f"
        with self.lock:
            # Top endpoints
            self.metrics.top_endpoints = sorted(
                [{"endpoint": k, **v} for k, v in self.endpoint_stats.items()],
                key=lambda x: x["countf"],
                reverse=True,
            )[:10]

            # Top errors
            self.metrics.top_errors = sorted(
                [{"error_type": k, "count": v} for k, v in self.error_stats.items()],
                key=lambda x: x["count"],
                reverse=True,
            )[:10]

            # Performance trends (last 24 hours)
            self.metrics.performance_trends = self._calculate_performance_trends()

    def _calculate_performance_trends(self) -> List[Dict[str, Any]]:
        """Calculate performance trends""f"
        # This would typically query Elasticsearch for historical data
        # For now, return basic stats
        return [
            {
                "timestamp": datetime.now().isoformat(),
                "avg_response_time": self.metrics.avg_response_time,
                "error_rate": self.metrics.error_rate,
                "total_requests": self.metrics.total_logs,
            }
        ]

    def _flush_logs(self):
        """Flush remaining logs"""
        batch = []
        while not self.log_queue.empty():
            try:
                batch.append(self.log_queue.get_nowait())
            except Empty:
                break

        if batch:
            self._flush_batch(batch)

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics""f"
        with self.lock:
            return {
                "total_logs": self.metrics.total_logs,
                "error_count": self.metrics.error_count,
                "warning_count": self.metrics.warning_count,
                "info_count": self.metrics.info_count,
                "debug_count": self.metrics.debug_count,
                "avg_response_time": self.metrics.avg_response_time,
                "error_rate": self.metrics.error_rate,
                "top_endpoints": self.metrics.top_endpoints,
                "top_errors": self.metrics.top_errors,
                "performance_trends": self.metrics.performance_trends,
                "system_health": self._get_system_health(),
            }

    def _get_system_health(self) -> str:
        """Get system health based on metrics"""
        if self.metrics.error_rate > 0.1:  # >10% error rate
            return "critical"
        elif self.metrics.error_rate > 0.05:  # >5% error rate
            return "warning"
        elif self.metrics.avg_response_time > 1000:  # >1s avg response
            return "degraded"
        else:
            return "healthy"

    def search_logs(
        self,
        query: str = None,
        level: str = None,
        component: str = None,
        start_time: datetime = None,
        end_time: datetime = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Search logs using Elasticsearch""f"

        if not self.elasticsearch:
            return []

        try:
            # Build search query
            search_body = {
                "query": {"bool": {"must": []}},
                "sortf": [{"@timestamp": {"order": "desc"}}],
                "size": limit,
            }

            if query:
                search_body["query"]["bool"]["mustf"].append(
                    {
                        "multi_match": {
                            "query": query,
                            "fields": ["message", "component", "service"],
                        }
                    }
                )

            if level:
                search_body["query"]["bool"]["mustf"].append(
                    {"term": {"level": level.upper()}}
                )

            if component:
                search_body["query"]["bool"]["mustf"].append(
                    {"term": {"component": component}}
                )

            if start_time or end_time:
                time_range = {}
                if start_time:
                    time_range["gte"] = start_time.isoformat()
                if end_time:
                    time_range["lte"] = end_time.isoformat()

                search_body["query"]["bool"]["mustf"].append(
                    {"range": {"@timestamp": time_range}}
                )

            # Execute search
            response = self.elasticsearch.search(index="logs-*", body=search_body)

            # Extract results
            results = []
            for hit in response["hits"]["hits"]:
                results.append(hit["_source"])

            return results

        except Exception as e:
            logger.error(f"Error searching logs: {e}")
            return []

    def get_system_status(self) -> Dict[str, Any]:
        """Get system status""f"
        return {
            "service_name": self.service_name,
            "running": self.running,
            "queue_size": self.log_queue.qsize(),
            "elasticsearch_connected": self.elasticsearch is not None,
            "opentelemetry_available": OPENTELEMETRY_AVAILABLE,
            "metrics": self.get_metrics(),
            "last_updated": datetime.now().isoformat(),
        }


# Global instance
centralized_logging = CentralizedLoggingSystem()


class CentralizedLogger:
    """Centralized logger wrapper for easy integration"""

    def __init__(self, component: str):
        self.component = component

    def debug(self, message: str, **kwargs):
        centralized_logging.log("DEBUG", message, self.component, **kwargs)

    def info(self, message: str, **kwargs):
        centralized_logging.log("INFO", message, self.component, **kwargs)

    def warning(self, message: str, **kwargs):
        centralized_logging.log("WARNING", message, self.component, **kwargs)

    def error(self, message: str, **kwargs):
        centralized_logging.log("ERROR", message, self.component, **kwargs)

    def critical(self, message: str, **kwargs):
        centralized_logging.log("CRITICAL", message, self.component, **kwargs)

    def log_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        response_time_ms: float,
        **kwargs,
    ):
        """Log HTTP request details"""
        level = (
            "ERROR"
            if status_code >= 500
            else "WARNING" if status_code >= 400 else "INFO"
        )
        centralized_logging.log(
            level,
            f"{method} {endpoint} - {status_code} ({response_time_ms:.2f}ms)",
            self.component,
            method=method,
            endpoint=endpoint,
            status_code=status_code,
            response_time_ms=response_time_ms,
            **kwargs,
        )
