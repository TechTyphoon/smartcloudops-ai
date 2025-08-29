"""
Production Health Checks and System Validation
Phase 2C Week 2: Production Deployment - Health Monitoring
"""

import asyncio
import json
import logging
import sqlite3
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import psutil
import requests

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health check status levels"""

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Individual health check result"""

    component: str
    status: HealthStatus
    message: str
    response_time: float
    timestamp: datetime
    details: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
        }


class BaseHealthCheck:
    """Base class for health checks"""

    def __init__(self, name: str, timeout: float = 5.0):
        self.name = name
        self.timeout = timeout

    async def check(self) -> HealthCheckResult:
        """Perform health check - to be implemented by subclasses"""
        raise NotImplementedError

    def _create_result(
        self,
        status: HealthStatus,
        message: str,
        response_time: float,
        details: Dict[str, Any] = None,
    ) -> HealthCheckResult:
        """Create standardized health check result"""
        return HealthCheckResult(
            component=self.name,
            status=status,
            message=message,
            response_time=response_time,
            timestamp=datetime.now(),
            details=details or {},
        )


class SystemResourcesCheck(BaseHealthCheck):
    """Check system resource utilization"""

    def __init__(
        self,
        cpu_threshold: float = 80.0,
        memory_threshold: float = 85.0,
        disk_threshold: float = 90.0,
    ):
        super().__init__("system_resources")
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.disk_threshold = disk_threshold

    async def check(self) -> HealthCheckResult:
        start_time = time.time()

        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # Disk usage
            disk = psutil.disk_usage("/")
            disk_percent = (disk.used / disk.total) * 100

            # Load average
            load_avg = psutil.getloadavg()

            details = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "disk_percent": disk_percent,
                "load_average": {
                    "1min": load_avg[0],
                    "5min": load_avg[1],
                    "15min": load_avg[2],
                },
                "memory_available_gb": memory.available / (1024**3),
                "disk_free_gb": disk.free / (1024**3),
            }

            # Determine status
            if (
                cpu_percent > self.cpu_threshold
                or memory_percent > self.memory_threshold
                or disk_percent > self.disk_threshold
            ):
                status = HealthStatus.CRITICAL
                message = f"High resource usage: CPU {cpu_percent:.1f}%, Memory {memory_percent:.1f}%, Disk {disk_percent:.1f}%"
            elif (
                cpu_percent > self.cpu_threshold * 0.8
                or memory_percent > self.memory_threshold * 0.8
                or disk_percent > self.disk_threshold * 0.8
            ):
                status = HealthStatus.WARNING
                message = f"Moderate resource usage: CPU {cpu_percent:.1f}%, Memory {memory_percent:.1f}%, Disk {disk_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Resources normal: CPU {cpu_percent:.1f}%, Memory {memory_percent:.1f}%, Disk {disk_percent:.1f}%"

            response_time = time.time() - start_time
            return self._create_result(status, message, response_time, details)

        except Exception as e:
            response_time = time.time() - start_time
            return self._create_result(
                HealthStatus.CRITICAL,
                f"System resources check failed: {str(e)}",
                response_time,
                {"error": str(e)},
            )


class DatabaseHealthCheck(BaseHealthCheck):
    """Check database connectivity and performance"""

    def __init__(self, db_path: str = "data/mlops_optimized.db"):
        super().__init__("database")
        self.db_path = db_path

    async def check(self) -> HealthCheckResult:
        start_time = time.time()

        try:
            # Check if database file exists
            db_file = Path(self.db_path)
            if not db_file.exists():
                response_time = time.time() - start_time
                return self._create_result(
                    HealthStatus.CRITICAL,
                    f"Database file not found: {self.db_path}",
                    response_time,
                    {"db_path": self.db_path, "exists": False},
                )

            # Test database connectivity
            conn = sqlite3.connect(self.db_path, timeout=5.0)
            cursor = conn.cursor()

            # Test basic query
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()

            # Get database size
            db_size = db_file.stat().st_size

            # Test write operation
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS health_check_test (id INTEGER, timestamp TEXT)"
            )
            cursor.execute(
                "INSERT INTO health_check_test (id, timestamp) VALUES (?, ?)",
                (1, datetime.now().isoformat()),
            )
            cursor.execute("DELETE FROM health_check_test WHERE id = ?", (1,))
            conn.commit()

            conn.close()

            details = {
                "db_path": self.db_path,
                "db_size_mb": db_size / (1024 * 1024),
                "table_count": len(tables),
                "tables": [table[0] for table in tables],
            }

            response_time = time.time() - start_time

            if response_time > 2.0:
                status = HealthStatus.WARNING
                message = f"Database slow response: {response_time:.3f}s"
            else:
                status = HealthStatus.HEALTHY
                message = f"Database operational: {response_time:.3f}s response"

            return self._create_result(status, message, response_time, details)

        except Exception as e:
            response_time = time.time() - start_time
            return self._create_result(
                HealthStatus.CRITICAL,
                f"Database check failed: {str(e)}",
                response_time,
                {"error": str(e), "db_path": self.db_path},
            )


class MLOpsServiceCheck(BaseHealthCheck):
    """Check MLOps service availability and functionality"""

    def __init__(self):
        super().__init__("mlops_service")

    async def check(self) -> HealthCheckResult:
        start_time = time.time()

        try:
            # Try to import MLOps service
            from app.services.mlops_service import MLOpsService

            # Create service instance
            service = MLOpsService()

            # Test basic operations
            experiments_available = service.experiment_tracker is not None
            models_available = service.model_registry is not None
            data_pipeline_available = service.data_pipeline is not None
            mlflow_available = service.mlflow_available

            # Test getting statistics
            try:
                stats = service.get_statistics()
                stats_working = stats is not None
            except Exception:
                stats_working = False

            details = {
                "experiment_tracker": experiments_available,
                "model_registry": models_available,
                "data_pipeline": data_pipeline_available,
                "mlflow": mlflow_available,
                "statistics": stats_working,
            }

            # Determine overall status
            core_components = [
                experiments_available,
                models_available,
                data_pipeline_available,
            ]
            working_components = sum(core_components)

            if working_components == 3 and stats_working:
                status = HealthStatus.HEALTHY
                message = "All MLOps components operational"
            elif working_components >= 2:
                status = HealthStatus.WARNING
                message = f"{working_components}/3 core components operational"
            else:
                status = HealthStatus.CRITICAL
                message = f"Only {working_components}/3 core components operational"

            response_time = time.time() - start_time
            return self._create_result(status, message, response_time, details)

        except Exception as e:
            response_time = time.time() - start_time
            return self._create_result(
                HealthStatus.CRITICAL,
                f"MLOps service check failed: {str(e)}",
                response_time,
                {"error": str(e)},
            )


class APIEndpointCheck(BaseHealthCheck):
    """Check API endpoint availability"""

    def __init__(self, base_url: str = "http://localhost:5000"):
        super().__init__("api_endpoints")
        self.base_url = base_url

    async def check(self) -> HealthCheckResult:
        start_time = time.time()

        try:
            # Test endpoints
            endpoints_to_test = [
                ("/", "root"),
                ("/api/status", "status"),
                ("/api/health", "health"),
            ]

            results = {}
            total_response_time = 0

            for endpoint, name in endpoints_to_test:
                try:
                    url = f"{self.base_url}{endpoint}"
                    response = requests.get(url, timeout=5.0)

                    endpoint_result = {
                        "status_code": response.status_code,
                        "response_time": response.elapsed.total_seconds(),
                        "success": response.status_code == 200,
                    }

                    total_response_time += endpoint_result["response_time"]
                    results[name] = endpoint_result

                except requests.RequestException as e:
                    results[name] = {"error": str(e), "success": False}

            # Check success rate
            successful_endpoints = sum(
                1 for result in results.values() if result.get("success", False)
            )
            total_endpoints = len(endpoints_to_test)
            success_rate = successful_endpoints / total_endpoints

            avg_response_time = total_response_time / max(successful_endpoints, 1)

            details = {
                "endpoints": results,
                "success_rate": success_rate,
                "avg_response_time": avg_response_time,
            }

            if success_rate == 1.0:
                status = HealthStatus.HEALTHY
                message = f"All {total_endpoints} endpoints responding"
            elif success_rate >= 0.8:
                status = HealthStatus.WARNING
                message = (
                    f"{successful_endpoints}/{total_endpoints} endpoints responding"
                )
            else:
                status = HealthStatus.CRITICAL
                message = f"Only {successful_endpoints}/{total_endpoints} endpoints responding"

            response_time = time.time() - start_time
            return self._create_result(status, message, response_time, details)

        except Exception as e:
            response_time = time.time() - start_time
            return self._create_result(
                HealthStatus.CRITICAL,
                f"API endpoint check failed: {str(e)}",
                response_time,
                {"error": str(e)},
            )


class CacheHealthCheck(BaseHealthCheck):
    """Check cache system health"""

    def __init__(self):
        super().__init__("cache_system")

    async def check(self) -> HealthCheckResult:
        start_time = time.time()

        try:
            # Try to import cache manager
            from app.performance.caching import cache_manager

            # Get cache statistics
            cache_stats = cache_manager.get_stats()

            # Test cache operations
            test_cache = cache_manager.get_cache("api_responses")
            if test_cache:
                # Test set and get
                test_key = f"health_check_{int(time.time())}"
                test_cache.set(test_key, "test_value", ttl=10)
                retrieved_value = test_cache.get(test_key)
                test_cache.delete(test_key)

                cache_operational = retrieved_value == "test_value"
            else:
                cache_operational = False

            # Analyze cache performance
            total_requests = 0
            total_hits = 0

            for cache_name, stats in cache_stats.items():
                total_requests += stats.get("hits", 0) + stats.get("misses", 0)
                total_hits += stats.get("hits", 0)

            hit_rate = total_hits / max(total_requests, 1)

            details = {
                "cache_stats": cache_stats,
                "operational": cache_operational,
                "overall_hit_rate": hit_rate,
                "total_requests": total_requests,
            }

            if cache_operational and hit_rate > 0.7:
                status = HealthStatus.HEALTHY
                message = f"Cache system operational with {hit_rate:.1%} hit rate"
            elif cache_operational:
                status = HealthStatus.WARNING
                message = f"Cache system operational but low hit rate: {hit_rate:.1%}"
            else:
                status = HealthStatus.CRITICAL
                message = "Cache system not operational"

            response_time = time.time() - start_time
            return self._create_result(status, message, response_time, details)

        except ImportError:
            response_time = time.time() - start_time
            return self._create_result(
                HealthStatus.WARNING,
                "Cache system not available (performance features disabled)",
                response_time,
                {"performance_features": False},
            )
        except Exception as e:
            response_time = time.time() - start_time
            return self._create_result(
                HealthStatus.CRITICAL,
                f"Cache system check failed: {str(e)}",
                response_time,
                {"error": str(e)},
            )


class HealthMonitor:
    """Comprehensive health monitoring system"""

    def __init__(self):
        self.checks = [
            SystemResourcesCheck(),
            DatabaseHealthCheck(),
            MLOpsServiceCheck(),
            CacheHealthCheck(),
        ]
        self.history: List[Dict[str, Any]] = []

    def add_check(self, check: BaseHealthCheck):
        """Add custom health check"""
        self.checks.append(check)

    async def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks and return comprehensive results"""
        results = []
        start_time = time.time()

        # Run all checks concurrently
        tasks = [check.check() for check in self.checks]
        check_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        overall_status = HealthStatus.HEALTHY
        component_statuses = {}

        for i, result in enumerate(check_results):
            if isinstance(result, Exception):
                # Handle check that failed with exception
                error_result = HealthCheckResult(
                    component=self.checks[i].name,
                    status=HealthStatus.CRITICAL,
                    message=f"Health check failed: {str(result)}",
                    response_time=0.0,
                    timestamp=datetime.now(),
                    details={"error": str(result)},
                )
                results.append(error_result)
                component_statuses[self.checks[i].name] = HealthStatus.CRITICAL
            else:
                results.append(result)
                component_statuses[result.component] = result.status

        # Determine overall status
        for status in component_statuses.values():
            if status == HealthStatus.CRITICAL:
                overall_status = HealthStatus.CRITICAL
                break
            elif (
                status == HealthStatus.WARNING
                and overall_status == HealthStatus.HEALTHY
            ):
                overall_status = HealthStatus.WARNING

        total_time = time.time() - start_time

        # Create comprehensive report
        report = {
            "overall_status": overall_status.value,
            "total_checks": len(self.checks),
            "healthy_checks": sum(
                1 for s in component_statuses.values() if s == HealthStatus.HEALTHY
            ),
            "warning_checks": sum(
                1 for s in component_statuses.values() if s == HealthStatus.WARNING
            ),
            "critical_checks": sum(
                1 for s in component_statuses.values() if s == HealthStatus.CRITICAL
            ),
            "total_response_time": total_time,
            "timestamp": datetime.now().isoformat(),
            "checks": [result.to_dict() for result in results],
        }

        # Store in history
        self.history.append(report)

        # Keep only last 100 reports
        if len(self.history) > 100:
            self.history = self.history[-100:]

        return report

    def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary from recent checks"""
        if not self.history:
            return {"status": "no_data", "message": "No health checks performed yet"}

        latest = self.history[-1]

        # Calculate uptime percentage from last 24 hours
        cutoff_time = datetime.now() - timedelta(hours=24)
        recent_reports = [
            report
            for report in self.history
            if datetime.fromisoformat(report["timestamp"]) > cutoff_time
        ]

        if recent_reports:
            healthy_reports = sum(
                1 for r in recent_reports if r["overall_status"] == "healthy"
            )
            uptime_percentage = (healthy_reports / len(recent_reports)) * 100
        else:
            uptime_percentage = None

        return {
            "current_status": latest["overall_status"],
            "last_check": latest["timestamp"],
            "uptime_24h": uptime_percentage,
            "total_checks_24h": len(recent_reports) if recent_reports else 0,
            "component_status": {
                check["component"]: check["status"] for check in latest["checks"]
            },
        }


# Global health monitor instance
health_monitor = HealthMonitor()


def add_api_endpoint_check(base_url: str):
    """Add API endpoint check for specific URL"""
    health_monitor.add_check(APIEndpointCheck(base_url))


async def quick_health_check() -> Dict[str, Any]:
    """Perform quick health check and return results"""
    return await health_monitor.run_all_checks()


def get_health_status() -> Dict[str, Any]:
    """Get current health status"""
    return health_monitor.get_health_summary()
