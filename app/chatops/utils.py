"""
Smart CloudOps AI - ChatOps Utilities
Helper functions for log retrieval, context gathering, and system utilities
"""

import os
import json
import logging
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class SystemContextGatherer:
    """Gather system context for ChatOps queries."""
    
    def __init__(self, prometheus_url: str = "http://localhost:9090"):
        """Initialize context gatherer."""
        self.prometheus_url = prometheus_url
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get current system health status."""
        try:
            # Check Flask application health
            flask_health = self._check_flask_health()
            
            # Check Prometheus connectivity
            prometheus_health = self._check_prometheus_health()
            
            return {
                "flask_app": flask_health,
                "prometheus": prometheus_health,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "overall_status": "healthy" if flask_health["status"] == "healthy" and prometheus_health["status"] == "healthy" else "degraded"
            }
        except Exception as e:
            logger.error(f"Error gathering system health: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def _check_flask_health(self) -> Dict[str, Any]:
        """Check Flask application health."""
        try:
            response = requests.get("http://localhost:3000/health", timeout=5)
            if response.status_code == 200:
                return {"status": "healthy", "response_time": response.elapsed.total_seconds()}
            else:
                return {"status": "unhealthy", "status_code": response.status_code}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    def _check_prometheus_health(self) -> Dict[str, Any]:
        """Check Prometheus connectivity."""
        try:
            response = requests.get(f"{self.prometheus_url}/-/healthy", timeout=5)
            if response.status_code == 200:
                return {"status": "healthy", "response_time": response.elapsed.total_seconds()}
            else:
                return {"status": "unhealthy", "status_code": response.status_code}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    def get_prometheus_metrics(self) -> Dict[str, Any]:
        """Get key Prometheus metrics."""
        try:
            # Get system metrics
            metrics = {}
            
            # CPU usage
            cpu_query = 'rate(node_cpu_seconds_total{mode!="idle"}[5m]) * 100'
            cpu_response = requests.get(f"{self.prometheus_url}/api/v1/query", params={"query": cpu_query}, timeout=10)
            if cpu_response.status_code == 200:
                cpu_data = cpu_response.json()
                if cpu_data["data"]["result"]:
                    metrics["cpu_usage"] = round(float(cpu_data["data"]["result"][0]["value"][1]), 2)
            
            # Memory usage
            mem_query = '(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100'
            mem_response = requests.get(f"{self.prometheus_url}/api/v1/query", params={"query": mem_query}, timeout=10)
            if mem_response.status_code == 200:
                mem_data = mem_response.json()
                if mem_data["data"]["result"]:
                    metrics["memory_usage"] = round(float(mem_data["data"]["result"][0]["value"][1]), 2)
            
            # Disk usage
            disk_query = '(1 - (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"})) * 100'
            disk_response = requests.get(f"{self.prometheus_url}/api/v1/query", params={"query": disk_query}, timeout=10)
            if disk_response.status_code == 200:
                disk_data = disk_response.json()
                if disk_data["data"]["result"]:
                    metrics["disk_usage"] = round(float(disk_data["data"]["result"][0]["value"][1]), 2)
            
            return {
                "status": "success",
                "metrics": metrics,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching Prometheus metrics: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def get_recent_alerts(self) -> List[Dict[str, Any]]:
        """Get recent alerts from Prometheus."""
        try:
            response = requests.get(f"{self.prometheus_url}/api/v1/alerts", timeout=10)
            if response.status_code == 200:
                alerts_data = response.json()
                recent_alerts = []
                
                for alert in alerts_data.get("data", {}).get("alerts", []):
                    if alert.get("state") in ["firing", "pending"]:
                        recent_alerts.append({
                            "name": alert.get("labels", {}).get("alertname", "Unknown"),
                            "state": alert.get("state"),
                            "severity": alert.get("labels", {}).get("severity", "unknown"),
                            "summary": alert.get("annotations", {}).get("summary", ""),
                            "description": alert.get("annotations", {}).get("description", "")
                        })
                
                return recent_alerts
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error fetching alerts: {str(e)}")
            return []
    
    def get_system_context(self) -> Dict[str, Any]:
        """Get comprehensive system context."""
        return {
            "system_health": self.get_system_health(),
            "prometheus_metrics": self.get_prometheus_metrics(),
            "recent_alerts": self.get_recent_alerts(),
            "resource_usage": self.get_prometheus_metrics().get("metrics", {}),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


class LogRetriever:
    """Retrieve and filter application logs."""
    
    def __init__(self, log_dir: str = "logs"):
        """Initialize log retriever."""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
    
    def get_recent_logs(self, hours: int = 24, level: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get recent logs with optional filtering."""
        try:
            logs = []
            cutoff_time = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=hours)
            
            # Get all log files
            log_files = list(self.log_dir.glob("*.log"))
            
            for log_file in log_files:
                try:
                    with open(log_file, 'r') as f:
                        for line in f:
                            try:
                                # Parse log line (assuming JSON format)
                                log_entry = json.loads(line.strip())
                                
                                # Parse timestamp
                                timestamp_str = log_entry.get("timestamp", "")
                                if timestamp_str:
                                    # Handle timezone-aware and naive timestamps
                                    if timestamp_str.endswith('Z'):
                                        log_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                                    else:
                                        log_time = datetime.fromisoformat(timestamp_str)
                                    
                                    # Make both timezone-naive for comparison
                                    if log_time.tzinfo is not None:
                                        log_time = log_time.replace(tzinfo=None)
                                    
                                    # Filter by time
                                    if log_time >= cutoff_time:
                                        # Filter by level if specified
                                        if level is None or log_entry.get("level", "").lower() == level.lower():
                                            logs.append(log_entry)
                            except json.JSONDecodeError:
                                # Skip non-JSON lines
                                continue
                except Exception as e:
                    logger.warning(f"Error reading log file {log_file}: {str(e)}")
                    continue
            
            # Sort by timestamp (newest first)
            logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            return logs[:100]  # Limit to 100 most recent entries
            
        except Exception as e:
            logger.error(f"Error retrieving logs: {str(e)}")
            return []
    
    def get_logs_by_service(self, service: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get logs for a specific service."""
        logs = self.get_recent_logs(hours=hours)
        return [log for log in logs if log.get("service", "").lower() == service.lower()]
    
    def get_error_logs(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get error-level logs."""
        return self.get_recent_logs(hours=hours, level="error")
    
    def create_sample_log(self, message: str, level: str = "info", service: str = "chatops"):
        """Create a sample log entry for testing."""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level.upper(),
            "service": service,
            "message": message,
            "module": "chatops.utils"
        }
        
        log_file = self.log_dir / f"{service}.log"
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        return log_entry


def validate_query_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and sanitize query parameters."""
    validated = {}
    
    # Validate hours parameter
    if "hours" in params:
        try:
            hours = int(params["hours"])
            if 1 <= hours <= 168:  # 1 hour to 1 week
                validated["hours"] = hours
            else:
                validated["hours"] = 24  # Default
        except (ValueError, TypeError):
            validated["hours"] = 24
    
    # Validate level parameter
    if "level" in params:
        level = str(params["level"]).lower()
        if level in ["debug", "info", "warning", "error", "critical"]:
            validated["level"] = level
    
    # Validate service parameter
    if "service" in params:
        service = str(params["service"]).strip()
        if service and len(service) <= 50:
            validated["service"] = service
    
    return validated


def format_response(data: Any, status: str = "success", message: str = "") -> Dict[str, Any]:
    """Format API response consistently."""
    return {
        "status": status,
        "data": data,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat()
    } 