#!/usr/bin/env python3
"""
GOD MODE: Real-Time Analytics Dashboard
Advanced real-time monitoring with WebSocket support, predictive analytics, and interactive visualizations
"""

import asyncio
import json
import logging
import os
import sqlite3
import threading
import time
import uuid
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Set

import numpy as np
import pandas as pd
import psutil
import websockets
from websockets.server import serve

# Import our systems
try:
    from app.logging.centralized_logging import centralized_logging

    # from ml_models.model_versioning import model_versioning

    LOGGING_AVAILABLE = True
except ImportError:
    LOGGING_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class SystemMetrics:
    """Real-time system metrics"""

    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    active_connections: int
    response_time_avg: float
    error_rate: float
    throughput: float
    queue_depth: int


@dataclass
class Alert:
    """System alert"""

    id: str
    timestamp: datetime
    severity: str  # 'info', 'warning', 'critical'
    category: str
    message: str
    details: Dict[str, Any]
    acknowledged: bool = False
    resolved: bool = False


@dataclass
class PredictiveInsight:
    """Predictive analytics insight"""

    timestamp: datetime
    insight_type: str  # 'anomaly', 'trend', 'forecast', 'recommendation'
    confidence: float
    message: str
    data: Dict[str, Any]
    actionable: bool = True


class RealTimeAnalyticsDashboard:
    """
    Advanced real-time analytics dashboard with WebSocket support
    """

    def __init__(
        self,
        host: str = os.getenv("APP_HOST", "0.0.0.0"),
        port: int = 8081,
        update_interval: float = 1.0,
        max_clients: int = 100,
    ):

        self.host = host
        self.port = port
        self.update_interval = update_interval
        self.max_clients = max_clients

        # WebSocket clients
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.client_lock = threading.Lock()

        # Metrics storage
        self.metrics_history = deque(maxlen=1000)  # Last 1000 data points
        self.alerts = deque(maxlen=100)  # Last 100 alerts
        self.insights = deque(maxlen=50)  # Last 50 insights

        # Performance tracking
        self.performance_data = defaultdict(lambda: deque(maxlen=100))
        self.anomaly_detection = AnomalyDetector()
        self.trend_analyzer = TrendAnalyzer()
        self.forecaster = TimeSeriesForecaster()

        # Threading
        self.running = False
        self.metrics_thread = None
        self.analytics_thread = None
        self.websocket_server = None

        # Database for persistence
        self.db_path = "analytics/dashboard.db"
        self._init_database()

        logger.info(f"Real-time analytics dashboard initialized on {host}:{port}")

    def _init_database(self):
        """Initialize SQLite database for analytics persistence"""
        import os

        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    cpu_usage REAL NOT NULL,
                    memory_usage REAL NOT NULL,
                    disk_usage REAL NOT NULL,
                    network_io TEXT NOT NULL,
                    active_connections INTEGER NOT NULL,
                    response_time_avg REAL NOT NULL,
                    error_rate REAL NOT NULL,
                    throughput REAL NOT NULL,
                    queue_depth INTEGER NOT NULL
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS alerts (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    category TEXT NOT NULL,
                    message TEXT NOT NULL,
                    details TEXT NOT NULL,
                    acknowledged BOOLEAN NOT NULL DEFAULT 0,
                    resolved BOOLEAN NOT NULL DEFAULT 0
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS insights (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    insight_type TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    message TEXT NOT NULL,
                    data TEXT NOT NULL,
                    actionable BOOLEAN NOT NULL DEFAULT 1
                )
            """
            )

            conn.commit()

    async def start(self):
        """Start the analytics dashboard"""
        if self.running:
            return

        self.running = True

        # Start background threads
        self.metrics_thread = threading.Thread(
            target=self._metrics_collector, daemon=True
        )
        self.metrics_thread.start()

        self.analytics_thread = threading.Thread(
            target=self._analytics_processor, daemon=True
        )
        self.analytics_thread.start()

        # Start WebSocket server
        self.websocket_server = await serve(
            self._websocket_handler, self.host, self.port
        )

        logger.info(
            f"Real-time analytics dashboard started on ws://{self.host}:{self.port}"
        )

    async def stop(self):
        """Stop the analytics dashboard"""
        self.running = False

        # Close WebSocket server
        if self.websocket_server:
            self.websocket_server.close()
            await self.websocket_server.wait_closed()

        # Wait for threads
        if self.metrics_thread:
            self.metrics_thread.join(timeout=5)

        if self.analytics_thread:
            self.analytics_thread.join(timeout=5)

        logger.info("Real-time analytics dashboard stopped")

    async def _websocket_handler(self, websocket, path):
        """Handle WebSocket connections"""
        client_id = str(uuid.uuid4())

        with self.client_lock:
            if len(self.clients) >= self.max_clients:
                await websocket.close(1013, "Maximum clients reached")
                return

            self.clients.add(websocket)

        logger.info(f"Client connected: {client_id}")

        try:
            # Send initial data
            await self._send_initial_data(websocket)

            # Keep connection alive and handle messages
            async for message in websocket:
                await self._handle_client_message(websocket, message, client_id)

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client disconnected: {client_id}")
        except Exception as e:
            logger.error(f"WebSocket error for client {client_id}: {e}")
        finally:
            with self.client_lock:
                self.clients.discard(websocket)

    async def _send_initial_data(self, websocket):
        """Send initial dashboard data to client"""
        data = {
            "type": "initial_data",
            "timestamp": datetime.now().isoformat(),
            "metrics": self._get_current_metrics(),
            "alerts": self._get_recent_alerts(),
            "insights": self._get_recent_insights(),
            "system_status": self._get_system_status(),
        }

        await websocket.send(json.dumps(data))

    async def _handle_client_message(self, websocket, message: str, client_id: str):
        """Handle client messages"""
        try:
            data = json.loads(message)
            message_type = data.get("type")

            if message_type == "subscribe":
                # Handle subscription to specific metrics
                await self._handle_subscription(websocket, data)
            elif message_type == "acknowledge_alert":
                # Handle alert acknowledgment
                await self._handle_alert_acknowledgment(data)
            elif message_type == "request_insights":
                # Handle insight requests
                await self._handle_insight_request(websocket, data)
            else:
                logger.warning(f"Unknown message type: {message_type}")

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON from client {client_id}")
        except Exception as e:
            logger.error(f"Error handling client message: {e}")

    async def _handle_subscription(self, websocket, data):
        """Handle metric subscriptions"""
        # Implementation for metric subscriptions
        pass

    async def _handle_alert_acknowledgment(self, data):
        """Handle alert acknowledgment"""
        alert_id = data.get("alert_id")
        if alert_id:
            self._acknowledge_alert(alert_id)

    async def _handle_insight_request(self, websocket, data):
        """Handle insight requests"""
        insight_type = data.get("insight_type", "all")
        insights = self._get_insights_by_type(insight_type)

        response = {
            "type": "insights_response",
            "insights": insights,
            "timestamp": datetime.now().isoformat(),
        }

        await websocket.send(json.dumps(response))

    def _metrics_collector(self):
        """Background thread for collecting system metrics"""
        while self.running:
            try:
                # Collect system metrics
                metrics = self._collect_system_metrics()
                self.metrics_history.append(metrics)

                # Store in database
                self._store_metrics(metrics)

                # Check for alerts
                self._check_alerts(metrics)

                # Generate insights
                self._generate_insights(metrics)

                # Broadcast to clients
                asyncio.run(self._broadcast_metrics(metrics))

                time.sleep(self.update_interval)

            except Exception as e:
                logger.error(f"Error in metrics collector: {e}")
                time.sleep(self.update_interval)

    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        # CPU usage
        cpu_usage = psutil.cpu_percent(interval=1)

        # Memory usage
        memory = psutil.virtual_memory()
        memory_usage = memory.percent

        # Disk usage
        disk = psutil.disk_usage("/")
        disk_usage = disk.percent

        # Network I/O
        network = psutil.net_io_counters()
        network_io = {
            "bytes_sent": network.bytes_sent,
            "bytes_recv": network.bytes_recv,
            "packets_sent": network.packets_sent,
            "packets_recv": network.packets_recv,
        }

        # Application-specific metrics
        active_connections = len(self.clients)
        response_time_avg = self._get_avg_response_time()
        error_rate = self._get_error_rate()
        throughput = self._get_throughput()
        queue_depth = self._get_queue_depth()

        return SystemMetrics(
            timestamp=datetime.now(),
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            disk_usage=disk_usage,
            network_io=network_io,
            active_connections=active_connections,
            response_time_avg=response_time_avg,
            error_rate=error_rate,
            throughput=throughput,
            queue_depth=queue_depth,
        )

    def _get_avg_response_time(self) -> float:
        """Get average response time"""
        if LOGGING_AVAILABLE:
            metrics = centralized_logging.get_metrics()
            return metrics.get("avg_response_time", 0.0)
        return 0.0

    def _get_error_rate(self) -> float:
        """Get current error rate"""
        if LOGGING_AVAILABLE:
            metrics = centralized_logging.get_metrics()
            return metrics.get("error_rate", 0.0)
        return 0.0

    def _get_throughput(self) -> float:
        """Get current throughput (requests per second)"""
        if LOGGING_AVAILABLE:
            metrics = centralized_logging.get_metrics()
            total_logs = metrics.get("total_logs", 0)
            # Calculate RPS based on recent activity
            return total_logs / 60.0 if total_logs > 0 else 0.0
        return 0.0

    def _get_queue_depth(self) -> int:
        """Get current queue depth"""
        if LOGGING_AVAILABLE:
            return centralized_logging.log_queue.qsize()
        return 0

    def _store_metrics(self, metrics: SystemMetrics):
        """Store metrics in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO system_metrics
                    (timestamp, cpu_usage, memory_usage, disk_usage, network_io,
                     active_connections, response_time_avg, error_rate, throughput, queue_depth)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        metrics.timestamp.isoformat(),
                        metrics.cpu_usage,
                        metrics.memory_usage,
                        metrics.disk_usage,
                        json.dumps(metrics.network_io),
                        metrics.active_connections,
                        metrics.response_time_avg,
                        metrics.error_rate,
                        metrics.throughput,
                        metrics.queue_depth,
                    ),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Error storing metrics: {e}")

    def _check_alerts(self, metrics: SystemMetrics):
        """Check for system alerts"""
        # CPU alert
        if metrics.cpu_usage > 90:
            self._create_alert(
                "critical",
                "system",
                f"High CPU usage: {metrics.cpu_usage:.1f}%",
                {"cpu_usage": metrics.cpu_usage},
            )
        elif metrics.cpu_usage > 80:
            self._create_alert(
                "warning",
                "system",
                f"Elevated CPU usage: {metrics.cpu_usage:.1f}%",
                {"cpu_usage": metrics.cpu_usage},
            )

        # Memory alert
        if metrics.memory_usage > 95:
            self._create_alert(
                "critical",
                "system",
                f"Critical memory usage: {metrics.memory_usage:.1f}%",
                {"memory_usage": metrics.memory_usage},
            )
        elif metrics.memory_usage > 85:
            self._create_alert(
                "warning",
                "system",
                f"High memory usage: {metrics.memory_usage:.1f}%",
                {"memory_usage": metrics.memory_usage},
            )

        # Disk alert
        if metrics.disk_usage > 95:
            self._create_alert(
                "critical",
                "system",
                f"Critical disk usage: {metrics.disk_usage:.1f}%",
                {"disk_usage": metrics.disk_usage},
            )
        elif metrics.disk_usage > 85:
            self._create_alert(
                "warning",
                "system",
                f"High disk usage: {metrics.disk_usage:.1f}%",
                {"disk_usage": metrics.disk_usage},
            )

        # Error rate alert
        if metrics.error_rate > 0.1:
            self._create_alert(
                "critical",
                "application",
                f"High error rate: {metrics.error_rate:.2%}",
                {"error_rate": metrics.error_rate},
            )
        elif metrics.error_rate > 0.05:
            self._create_alert(
                "warning",
                "application",
                f"Elevated error rate: {metrics.error_rate:.2%}",
                {"error_rate": metrics.error_rate},
            )

    def _create_alert(
        self, severity: str, category: str, message: str, details: Dict[str, Any]
    ):
        """Create a new alert"""
        alert = Alert(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            severity=severity,
            category=category,
            message=message,
            details=details,
        )

        self.alerts.append(alert)

        # Store in database
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO alerts (id, timestamp, severity, category, message, details)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        alert.id,
                        alert.timestamp.isoformat(),
                        alert.severity,
                        alert.category,
                        alert.message,
                        json.dumps(alert.details),
                    ),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Error storing alert: {e}")

    def _acknowledge_alert(self, alert_id: str):
        """Acknowledge an alert"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "UPDATE alerts SET acknowledged = 1 WHERE id = ?", (alert_id,)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Error acknowledging alert: {e}")

    def _analytics_processor(self):
        """Background thread for analytics processing"""
        while self.running:
            try:
                # Analyze recent metrics for insights
                if len(self.metrics_history) >= 10:
                    recent_metrics = list(self.metrics_history)[-10:]
                    insights = self._analyze_metrics(recent_metrics)

                    for insight in insights:
                        self.insights.append(insight)
                        self._store_insight(insight)

                time.sleep(30)  # Process every 30 seconds

            except Exception as e:
                logger.error(f"Error in analytics processor: {e}")
                time.sleep(30)

    def _analyze_metrics(
        self, metrics_list: List[SystemMetrics]
    ) -> List[PredictiveInsight]:
        """Analyze metrics for insights"""
        insights = []

        # Convert to DataFrame for analysis
        df = pd.DataFrame([asdict(m) for m in metrics_list])

        # Trend analysis
        cpu_trend = self.trend_analyzer.analyze_trend(df["cpu_usage"].values)
        if cpu_trend["trend"] == "increasing" and cpu_trend["slope"] > 0.5:
            insights.append(
                PredictiveInsight(
                    timestamp=datetime.now(),
                    insight_type="trend",
                    confidence=cpu_trend["confidence"],
                    message="CPU usage showing upward trend",
                    data=cpu_trend,
                )
            )

        # Anomaly detection
        cpu_anomalies = self.anomaly_detection.detect_anomalies(df["cpu_usage"].values)
        if cpu_anomalies["anomalies"]:
            insights.append(
                PredictiveInsight(
                    timestamp=datetime.now(),
                    insight_type="anomaly",
                    confidence=cpu_anomalies["confidence"],
                    message="CPU usage anomalies detected",
                    data=cpu_anomalies,
                )
            )

        # Forecasting
        if len(df) >= 20:
            forecast = self.forecaster.forecast(df["cpu_usage"].values, steps=5)
            insights.append(
                PredictiveInsight(
                    timestamp=datetime.now(),
                    insight_type="forecast",
                    confidence=forecast["confidence"],
                    message="CPU usage forecast available",
                    data=forecast,
                )
            )

        return insights

    def _store_insight(self, insight: PredictiveInsight):
        """Store insight in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO insights (id, timestamp, insight_type, confidence, message, data, actionable)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        str(uuid.uuid4()),
                        insight.timestamp.isoformat(),
                        insight.insight_type,
                        insight.confidence,
                        insight.message,
                        json.dumps(insight.data),
                        insight.actionable,
                    ),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Error storing insight: {e}")

    async def _broadcast_metrics(self, metrics: SystemMetrics):
        """Broadcast metrics to all connected clients"""
        if not self.clients:
            return

        data = {
            "type": "metrics_update",
            "timestamp": metrics.timestamp.isoformat(),
            "metrics": asdict(metrics),
        }

        message = json.dumps(data)
        disconnected_clients = set()

        with self.client_lock:
            for client in self.clients:
                try:
                    await client.send(message)
                except websockets.exceptions.ConnectionClosed:
                    disconnected_clients.add(client)
                except Exception as e:
                    logger.error(f"Error sending to client: {e}")
                    disconnected_clients.add(client)

            # Remove disconnected clients
            self.clients -= disconnected_clients

    def _get_current_metrics(self) -> Dict[str, Any]:
        """Get current metrics for dashboard"""
        if self.metrics_history:
            latest = self.metrics_history[-1]
            return asdict(latest)
        return {}

    def _get_recent_alerts(self) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        return [asdict(alert) for alert in list(self.alerts)[-10:]]

    def _get_recent_insights(self) -> List[Dict[str, Any]]:
        """Get recent insights"""
        return [asdict(insight) for insight in list(self.insights)[-5:]]

    def _get_insights_by_type(self, insight_type: str) -> List[Dict[str, Any]]:
        """Get insights by type"""
        if insight_type == "all":
            return self._get_recent_insights()

        filtered = [
            insight for insight in self.insights if insight.insight_type == insight_type
        ]
        return [asdict(insight) for insight in filtered[-10:]]

    def _get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        if not self.metrics_history:
            return {"status": "unknown", "message": "No metrics available"}

        latest = self.metrics_history[-1]

        # Determine overall status
        if (
            latest.cpu_usage > 90
            or latest.memory_usage > 95
            or latest.disk_usage > 95
            or latest.error_rate > 0.1
        ):
            status = "critical"
        elif (
            latest.cpu_usage > 80
            or latest.memory_usage > 85
            or latest.disk_usage > 85
            or latest.error_rate > 0.05
        ):
            status = "warning"
        else:
            status = "healthy"

        return {
            "status": status,
            "timestamp": latest.timestamp.isoformat(),
            "active_clients": len(self.clients),
            "metrics_count": len(self.metrics_history),
            "alerts_count": len(self.alerts),
            "insights_count": len(self.insights),
        }


class AnomalyDetector:
    """Simple anomaly detection for metrics"""

    def detect_anomalies(self, values: List[float]) -> Dict[str, Any]:
        """Detect anomalies in time series data"""
        if len(values) < 5:
            return {"anomalies": [], "confidence": 0.0}

        mean = np.mean(values)
        std = np.std(values)

        anomalies = []
        for i, value in enumerate(values):
            if abs(value - mean) > 2 * std:  # 2-sigma rule
                anomalies.append(
                    {"index": i, "value": value, "deviation": abs(value - mean)}
                )

        confidence = len(anomalies) / len(values) if values else 0.0

        return {
            "anomalies": anomalies,
            "confidence": confidence,
            "mean": mean,
            "std": std,
        }


class TrendAnalyzer:
    """Simple trend analysis for metrics"""

    def analyze_trend(self, values: List[float]) -> Dict[str, Any]:
        """Analyze trend in time series data"""
        if len(values) < 3:
            return {"trend": "unknown", "slope": 0.0, "confidence": 0.0}

        x = np.arange(len(values))
        slope, intercept = np.polyfit(x, values, 1)

        # Calculate R-squared for confidence
        y_pred = slope * x + intercept
        ss_res = np.sum((values - y_pred) ** 2)
        ss_tot = np.sum((values - np.mean(values)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

        if abs(slope) < 0.1:
            trend = "stable"
        elif slope > 0:
            trend = "increasing"
        else:
            trend = "decreasing"

        return {
            "trend": trend,
            "slope": slope,
            "confidence": r_squared,
            "intercept": intercept,
        }


class TimeSeriesForecaster:
    """Simple time series forecasting"""

    def forecast(self, values: List[float], steps: int = 5) -> Dict[str, Any]:
        """Forecast future values"""
        if len(values) < 10:
            return {"forecast": [], "confidence": 0.0}

        # Simple linear regression forecast
        x = np.arange(len(values))
        slope, intercept = np.polyfit(x, values, 1)

        future_x = np.arange(len(values), len(values) + steps)
        forecast_values = slope * future_x + intercept

        # Calculate confidence based on recent variance
        recent_variance = np.var(values[-5:]) if len(values) >= 5 else np.var(values)
        confidence = max(0.0, 1.0 - recent_variance / 100.0)  # Normalize confidence

        return {
            "forecast": forecast_values.tolist(),
            "confidence": confidence,
            "slope": slope,
            "steps": steps,
        }


# Global instance
analytics_dashboard = RealTimeAnalyticsDashboard()
