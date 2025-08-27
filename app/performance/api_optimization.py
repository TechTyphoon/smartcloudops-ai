"""
API Performance Optimization and Monitoring
Phase 2C Week 1: Performance & Scaling - API Layer
"""

import gc
import logging
import threading
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

import psutil
from flask import Flask, g, jsonify, request

from .caching import cache_manager, cache_performance_monitor, cached
from .database_optimization import get_optimized_database

logger = logging.getLogger(__name__)


@dataclass
class APIMetrics:
    """API performance metrics"""

    endpoint: str
    method: str
    status_code: int
    response_time: float
    response_size: int
    timestamp: datetime
    user_agent: str
    ip_address: str
    memory_usage: float
    cpu_usage: float


class PerformanceCollector:
    """Collect and analyze API performance metrics"""

    def __init__(self, max_metrics: int = 10000):
        self.metrics: deque[APIMetrics] = deque(maxlen=max_metrics)
        self.endpoint_stats: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self._lock = threading.Lock()

        # Real-time aggregations
        self.current_minute_requests = 0
        self.current_minute_start = time.time()

        # Resource monitoring
        self.process = psutil.Process()

    def record_request(self, metrics: APIMetrics):
        """Record API request metrics"""
        with self._lock:
            self.metrics.append(metrics)

            # Update endpoint statistics
            endpoint_key = f"{metrics.method} {metrics.endpoint}"
            stats = self.endpoint_stats[endpoint_key]

            if "count" not in stats:
                stats.update(
                    {
                        "count": 0,
                        "total_time": 0.0,
                        "min_time": float("inf"),
                        "max_time": 0.0,
                        "status_codes": defaultdict(int),
                        "avg_response_time": 0.0,
                        "error_rate": 0.0,
                        "avg_response_size": 0.0,
                        "total_response_size": 0,
                    }
                )

            # Update statistics
            stats["count"] += 1
            stats["total_time"] += metrics.response_time
            stats["min_time"] = min(stats["min_time"], metrics.response_time)
            stats["max_time"] = max(stats["max_time"], metrics.response_time)
            stats["status_codes"][metrics.status_code] += 1
            stats["total_response_size"] += metrics.response_size

            # Calculate derived metrics
            stats["avg_response_time"] = stats["total_time"] / stats["count"]
            stats["avg_response_size"] = stats["total_response_size"] / stats["count"]

            error_count = sum(
                count for code, count in stats["status_codes"].items() if code >= 400
            )
            stats["error_rate"] = error_count / stats["count"]

            # Update current minute counter
            current_time = time.time()
            if current_time - self.current_minute_start > 60:
                self.current_minute_requests = 1
                self.current_minute_start = current_time
            else:
                self.current_minute_requests += 1

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system resource metrics"""
        try:
            memory_info = self.process.memory_info()
            cpu_percent = self.process.cpu_percent()

            return {
                "memory": {
                    "rss": memory_info.rss,
                    "vms": memory_info.vms,
                    "rss_mb": memory_info.rss / 1024 / 1024,
                    "percent": self.process.memory_percent(),
                },
                "cpu": {
                    "percent": cpu_percent,
                    "num_threads": self.process.num_threads(),
                },
                "requests": {
                    "current_minute": self.current_minute_requests,
                    "total": len(self.metrics),
                },
            }
        except Exception as e:
            logger.warning(f"Failed to get system metrics: {e}")
            return {}

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        if not self.metrics:
            return {}

        # Calculate overall statistics
        recent_metrics = list(self.metrics)[-1000:]  # Last 1000 requests
        response_times = [m.response_time for m in recent_metrics]
        response_sizes = [m.response_size for m in recent_metrics]

        # Calculate percentiles
        sorted_times = sorted(response_times)
        p50_idx = int(len(sorted_times) * 0.5)
        p95_idx = int(len(sorted_times) * 0.95)
        p99_idx = int(len(sorted_times) * 0.99)

        return {
            "overall": {
                "total_requests": len(self.metrics),
                "avg_response_time": sum(response_times) / len(response_times),
                "p50_response_time": sorted_times[p50_idx] if sorted_times else 0,
                "p95_response_time": sorted_times[p95_idx] if sorted_times else 0,
                "p99_response_time": sorted_times[p99_idx] if sorted_times else 0,
                "avg_response_size": sum(response_sizes) / len(response_sizes),
                "requests_per_minute": self.current_minute_requests,
            },
            "endpoints": dict(self.endpoint_stats),
            "system": self.get_system_metrics(),
            "cache": cache_manager.get_stats(),
            "database": (
                get_database().get_performance_report() if get_database() else {}
            ),
        }

    def get_slow_endpoints(self, threshold: float = 1.0) -> List[Dict[str, Any]]:
        """Get endpoints with response times above threshold"""
        slow_endpoints = []

        for endpoint, stats in self.endpoint_stats.items():
            if stats.get("avg_response_time", 0) > threshold:
                slow_endpoints.append(
                    {
                        "endpoint": endpoint,
                        "avg_response_time": stats["avg_response_time"],
                        "max_response_time": stats["max_time"],
                        "request_count": stats["count"],
                        "error_rate": stats["error_rate"],
                    }
                )

        return sorted(
            slow_endpoints, key=lambda x: x["avg_response_time"], reverse=True
        )


# Global performance collector
performance_collector = PerformanceCollector()


class ResponseCompression:
    """HTTP response compression utility"""

    @staticmethod
    def should_compress(response_data: str, min_size: int = 1000) -> bool:
        """Check if response should be compressed"""
        return len(response_data) > min_size

    @staticmethod
    def compress_response(data: str) -> bytes:
        """Compress response data"""
        import gzip

        return gzip.compress(data.encode("utf-8"))


class RateLimiter:
    """Simple in-memory rate limiter"""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, deque] = defaultdict(lambda: deque())
        self._lock = threading.Lock()

    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed for identifier"""
        current_time = time.time()

        with self._lock:
            request_times = self.requests[identifier]

            # Remove old requests outside window
            while (
                request_times and current_time - request_times[0] > self.window_seconds
            ):
                request_times.popleft()

            # Check if under limit
            if len(request_times) < self.max_requests:
                request_times.append(current_time)
                return True

            return False

    def get_remaining(self, identifier: str) -> int:
        """Get remaining requests for identifier"""
        current_time = time.time()

        with self._lock:
            request_times = self.requests[identifier]

            # Remove old requests
            while (
                request_times and current_time - request_times[0] > self.window_seconds
            ):
                request_times.popleft()

            return max(0, self.max_requests - len(request_times))


# Global rate limiter
rate_limiter = RateLimiter()


def performance_middleware(app: Flask):
    """Flask middleware for performance monitoring"""

    @app.before_request
    def before_request():
        g.start_time = time.time()
        g.start_memory = performance_collector.process.memory_info().rss

    @app.after_request
    def after_request(response):
        try:
            # Calculate metrics
            end_time = time.time()
            response_time = end_time - g.start_time
            end_memory = performance_collector.process.memory_info().rss
            memory_delta = end_memory - g.start_memory

            # Get response size
            response_size = len(response.get_data())

            # Record metrics
            metrics = APIMetrics(
                endpoint=request.endpoint or request.path,
                method=request.method,
                status_code=response.status_code,
                response_time=response_time,
                response_size=response_size,
                timestamp=datetime.now(),
                user_agent=request.headers.get("User-Agent", ""),
                ip_address=request.remote_addr or "",
                memory_usage=memory_delta,
                cpu_usage=performance_collector.process.cpu_percent(),
            )

            performance_collector.record_request(metrics)

            # Add performance headers
            response.headers["X-Response-Time"] = f"{response_time:.3f}s"
            response.headers["X-Memory-Delta"] = f"{memory_delta / 1024 / 1024:.2f}MB"

            # Log slow requests
            if response_time > 2.0:
                logger.warning(
                    f"Slow request: {request.method} {request.path} "
                    f"took {response_time:.3f}s"
                )

        except Exception as e:
            logger.error(f"Performance middleware error: {e}")

        return response

    @app.route("/api/performance/metrics")
    def performance_metrics():
        """Endpoint to get performance metrics"""
        try:
            summary = performance_collector.get_performance_summary()
            return jsonify({"status": "success", "data": summary, "error": None})
        except Exception as e:
            return jsonify({"status": "error", "data": None, "error": str(e)}), 500

    @app.route("/api/performance/slow-endpoints")
    def slow_endpoints():
        """Endpoint to get slow endpoints"""
        try:
            threshold = float(request.args.get("threshold", 1.0))
            slow = performance_collector.get_slow_endpoints(threshold)
            return jsonify({"status": "success", "data": slow, "error": None})
        except Exception as e:
            return jsonify({"status": "error", "data": None, "error": str(e)}), 500


def optimize_response(cache_ttl: int = 300, compress: bool = True):
    """Decorator for response optimization"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check rate limiting
            client_ip = request.remote_addr or "unknown"
            if not rate_limiter.is_allowed(client_ip):
                return (
                    jsonify(
                        {
                            "status": "error",
                            "data": None,
                            "error": "Rate limit exceeded",
                        }
                    ),
                    429,
                )

            # Try cache first
            cache_key = (
                f"{request.method}:{request.path}:{request.query_string.decode()}"
            )
            cached_response = cache_manager.get_cache("api_responses")

            if cached_response:
                result = cached_response.get(cache_key)
                if result:
                    response = jsonify(result)
                    response.headers["X-Cache"] = "HIT"
                    return response

            # Execute function
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time

            # Cache result if successful
            if hasattr(result, "status_code") and result.status_code == 200:
                if cached_response:
                    cached_response.set(cache_key, result.get_json(), ttl=cache_ttl)

            # Add performance headers
            if hasattr(result, "headers"):
                result.headers["X-Cache"] = "MISS"
                result.headers["X-Execution-Time"] = f"{execution_time:.3f}s"
                result.headers["X-Rate-Limit-Remaining"] = str(
                    rate_limiter.get_remaining(client_ip)
                )

            return result

        return wrapper

    return decorator


class MemoryManager:
    """Memory management utilities"""

    @staticmethod
    def cleanup_memory():
        """Force garbage collection and memory cleanup"""
        import gc

        collected = gc.collect()
        logger.info(f"Garbage collected {collected} objects")
        return collected

    @staticmethod
    def get_memory_usage() -> Dict[str, Any]:
        """Get detailed memory usage information"""
        try:
            import tracemalloc

            process = psutil.Process()
            memory_info = process.memory_info()

            # Get Python object memory if tracemalloc is running
            python_memory = {}
            if tracemalloc.is_tracing():
                current, peak = tracemalloc.get_traced_memory()
                python_memory = {
                    "current": current,
                    "peak": peak,
                    "current_mb": current / 1024 / 1024,
                    "peak_mb": peak / 1024 / 1024,
                }

            return {
                "system": {
                    "rss": memory_info.rss,
                    "vms": memory_info.vms,
                    "rss_mb": memory_info.rss / 1024 / 1024,
                    "percent": process.memory_percent(),
                },
                "python": python_memory,
                "gc_stats": {"counts": gc.get_count(), "threshold": gc.get_threshold()},
            }
        except Exception as e:
            logger.error(f"Failed to get memory usage: {e}")
            return {}

    @staticmethod
    def start_memory_monitoring():
        """Start memory monitoring"""
        try:
            import tracemalloc

            tracemalloc.start()
            logger.info("Memory monitoring started")
        except Exception as e:
            logger.warning(f"Failed to start memory monitoring: {e}")


class BackgroundOptimizer:
    """Background optimization tasks"""

    def __init__(self):
        self.running = False
        self.thread: Optional[threading.Thread] = None

    def start(self):
        """Start background optimization"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._optimization_loop, daemon=True)
            self.thread.start()
            logger.info("Background optimizer started")

    def stop(self):
        """Stop background optimization"""
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("Background optimizer stopped")

    def _optimization_loop(self):
        """Main optimization loop"""
        while self.running:
            try:
                # Run optimization tasks every 5 minutes
                time.sleep(300)

                # Memory cleanup
                MemoryManager.cleanup_memory()

                # Cache cleanup (remove expired entries)
                for cache_name, cache in cache_manager.caches.items():
                    if hasattr(cache, "_evict_expired"):
                        cache._evict_expired()

                # Database optimization (if needed)
                try:
                    db = get_database()
                    if db:
                        # Analyze slow queries
                        slow_queries = db.metrics.get_slow_queries(threshold=2.0)
                        if len(slow_queries) > 10:
                            logger.warning(f"Found {len(slow_queries)} slow queries")
                except Exception as e:
                    logger.debug(f"Database optimization check failed: {e}")

                logger.debug("Background optimization cycle completed")

            except Exception as e:
                logger.error(f"Background optimization error: {e}")


# Global background optimizer
background_optimizer = BackgroundOptimizer()


def init_performance_monitoring(app: Flask):
    """Initialize performance monitoring for Flask app"""

    # Add middleware
    performance_middleware(app)

    # Start memory monitoring
    MemoryManager.start_memory_monitoring()

    # Start background optimizer
    background_optimizer.start()

    logger.info("Performance monitoring initialized")


def shutdown_performance_monitoring():
    """Shutdown performance monitoring"""
    background_optimizer.stop()
    logger.info("Performance monitoring shutdown")
