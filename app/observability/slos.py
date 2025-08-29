"""
Service Level Objectives (SLO) Monitoring Module
SLO tracking and alerting
"""

import time
from datetime import datetime, timezone
from typing import Dict, List, Optional


class SLOManager:
    """Service Level Objectives manager"""

    def __init__(self):
        self.slos = {}
        self.metrics = {}
        self.alerts = []

        # Initialize default SLOs
        self._setup_default_slos()

    def _setup_default_slos(self):
        """Setup default SLOs for SmartCloudOps AI"""
        self.add_slo(
            name="availability",
            target=99.9,
            window_hours=24,
            description="Service availability percentage",
        )

        self.add_slo(
            name="response_time",
            target=200,  # ms
            window_hours=1,
            description="Average response time in milliseconds",
        )

        self.add_slo(
            name="error_rate",
            target=0.1,  # 0.1%
            window_hours=1,
            description="Error rate percentage",
        )

        self.add_slo(
            name="throughput",
            target=1000,  # requests per second
            window_hours=1,
            description="Requests per second",
        )

    def add_slo(
        self, name: str, target: float, window_hours: int, description: str = ""
    ):
        """Add a new SLO"""
        self.slos[name] = {
            "target": target,
            "window_hours": window_hours,
            "description": description,
            "created_at": datetime.now(timezone.utc),
        }

    def record_metric(
        self, slo_name: str, value: float, timestamp: Optional[datetime] = None
    ):
        """Record a metric for an SLO"""
        if slo_name not in self.slos:
            raise ValueError(f"SLO '{slo_name}' not found")

        if timestamp is None:
            timestamp = datetime.now(timezone.utc)

        if slo_name not in self.metrics:
            self.metrics[slo_name] = []

        self.metrics[slo_name].append({"value": value, "timestamp": timestamp})

        # Clean old metrics
        self._cleanup_old_metrics(slo_name)

    def _cleanup_old_metrics(self, slo_name: str):
        """Remove metrics older than the SLO window"""
        if slo_name not in self.slos or slo_name not in self.metrics:
            return

        window_hours = self.slos[slo_name]["window_hours"]
        cutoff_time = datetime.now(timezone.utc) - time.timedelta(hours=window_hours)

        self.metrics[slo_name] = [
            metric
            for metric in self.metrics[slo_name]
            if metric["timestamp"] > cutoff_time
        ]

    def get_slo_status(
        self, slo_name: str, current_value: Optional[float] = None
    ) -> Dict:
        """Get current status of an SLO"""
        if slo_name not in self.slos:
            return {"error": f"SLO '{slo_name}' not found"}

        slo = self.slos[slo_name]
        target = slo["target"]

        # Calculate current value if not provided
        if current_value is None:
            current_value = self._calculate_current_value(slo_name)

        # Determine status
        if slo_name == "error_rate":
            # For error rate, lower is better
            if current_value <= target:
                status = "meeting"
            elif current_value <= target * 2:
                status = "warning"
            else:
                status = "alert"
        else:
            # For other metrics, higher is better
            if current_value >= target:
                status = "meeting"
            elif current_value >= target * 0.8:
                status = "warning"
            else:
                status = "alert"

        return {
            "name": slo_name,
            "target": target,
            "current_value": current_value,
            "status": status,
            "description": slo["description"],
            "window_hours": slo["window_hours"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _calculate_current_value(self, slo_name: str) -> float:
        """Calculate current value for an SLO based on recent metrics"""
        if slo_name not in self.metrics or not self.metrics[slo_name]:
            return 0.0

        values = [metric["value"] for metric in self.metrics[slo_name]]

        if slo_name == "availability":
            # Calculate availability percentage
            return sum(1 for v in values if v > 0) / len(values) * 100
        elif slo_name == "error_rate":
            # Calculate error rate percentage
            return sum(1 for v in values if v > 0) / len(values) * 100
        else:
            # Calculate average for other metrics
            return sum(values) / len(values)

    def get_all_slo_status(self) -> Dict[str, Dict]:
        """Get status of all SLOs"""
        return {name: self.get_slo_status(name) for name in self.slos.keys()}

    def generate_alerts(self) -> List[Dict]:
        """Generate alerts for SLOs that are not meeting targets"""
        alerts = []

        for slo_name in self.slos:
            status = self.get_slo_status(slo_name)
            if status.get("status") in ["warning", "alert"]:
                alerts.append(
                    {
                        "slo_name": slo_name,
                        "status": status["status"],
                        "current_value": status["current_value"],
                        "target": status["target"],
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                )

        return alerts


# Global SLO manager instance
slo_manager = SLOManager()


def setup_slo_monitoring(app) -> None:
    """Setup SLO monitoring for the application"""
    # SLO manager is already initialized
    app.logger.info("SLO monitoring initialized")


def get_slo_manager() -> SLOManager:
    """Get the global SLO manager instance"""
    return slo_manager


def get_slo_status(slo_name: str, current_value: Optional[float] = None) -> Dict:
    """Get status of a specific SLO"""
    return slo_manager.get_slo_status(slo_name, current_value)


def get_all_slo_status() -> Dict[str, Dict]:
    """Get status of all SLOs"""
    return slo_manager.get_all_slo_status()


def generate_slo_alerts() -> List[Dict]:
    """Generate alerts for SLOs not meeting targets"""
    return slo_manager.generate_alerts()
