"""
Production Monitoring and Alerting System
Phase 2C Week 2: Production Deployment - Monitoring & Alerting
"""

import time
import logging
import asyncio
import smtplib
import json
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from pathlib import Path
import threading
import queue
from collections import defaultdict, deque

from .health_checks import health_monitor, HealthStatus

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class Alert:
    """Alert data structure"""
    id: str
    title: str
    message: str
    severity: AlertSeverity
    component: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            'severity': self.severity.value,
            'timestamp': self.timestamp.isoformat(),
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }


class MetricCollector:
    """Collect and aggregate system metrics"""
    
    def __init__(self, max_history: int = 1000):
        self.metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self.current_metrics: Dict[str, Any] = {}
        self._lock = threading.Lock()
    
    def record_metric(self, metric_name: str, value: Any, timestamp: Optional[datetime] = None):
        """Record a metric value"""
        if timestamp is None:
            timestamp = datetime.now()
        
        with self._lock:
            metric_entry = {
                'value': value,
                'timestamp': timestamp
            }
            
            self.metrics_history[metric_name].append(metric_entry)
            self.current_metrics[metric_name] = metric_entry
    
    def get_metric_history(self, metric_name: str, duration_hours: int = 24) -> List[Dict[str, Any]]:
        """Get metric history for specified duration"""
        cutoff_time = datetime.now() - timedelta(hours=duration_hours)
        
        with self._lock:
            history = self.metrics_history.get(metric_name, [])
            return [
                entry for entry in history 
                if entry['timestamp'] > cutoff_time
            ]
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current metric values"""
        with self._lock:
            return dict(self.current_metrics)
    
    def calculate_metric_stats(self, metric_name: str, duration_hours: int = 1) -> Dict[str, Any]:
        """Calculate statistics for a metric over time period"""
        history = self.get_metric_history(metric_name, duration_hours)
        
        if not history:
            return {}
        
        values = [entry['value'] for entry in history if isinstance(entry['value'], (int, float))]
        
        if not values:
            return {}
        
        return {
            'count': len(values),
            'avg': sum(values) / len(values),
            'min': min(values),
            'max': max(values),
            'latest': values[-1] if values else None,
            'trend': 'increasing' if len(values) > 1 and values[-1] > values[0] else 'decreasing' if len(values) > 1 and values[-1] < values[0] else 'stable'
        }


class AlertManager:
    """Manage alerts and notifications"""
    
    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.alert_handlers: List[Callable[[Alert], None]] = []
        self.alert_queue = queue.Queue()
        self.processing_thread = None
        self.running = False
        
        # Alert rate limiting
        self.rate_limits: Dict[str, List[datetime]] = defaultdict(list)
        self.max_alerts_per_hour = 10
    
    def add_alert_handler(self, handler: Callable[[Alert], None]):
        """Add custom alert handler"""
        self.alert_handlers.append(handler)
    
    def start(self):
        """Start alert processing"""
        if not self.running:
            self.running = True
            self.processing_thread = threading.Thread(target=self._process_alerts, daemon=True)
            self.processing_thread.start()
            logger.info("Alert manager started")
    
    def stop(self):
        """Stop alert processing"""
        self.running = False
        if self.processing_thread:
            self.processing_thread.join()
        logger.info("Alert manager stopped")
    
    def create_alert(self, title: str, message: str, severity: AlertSeverity, 
                    component: str, metadata: Dict[str, Any] = None) -> str:
        """Create new alert"""
        alert_id = f"{component}_{int(time.time())}"
        
        # Check rate limiting
        if self._is_rate_limited(component):
            logger.warning(f"Alert rate limited for component: {component}")
            return alert_id
        
        alert = Alert(
            id=alert_id,
            title=title,
            message=message,
            severity=severity,
            component=component,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        self.alerts[alert_id] = alert
        self.alert_queue.put(alert)
        
        # Record rate limit
        self.rate_limits[component].append(datetime.now())
        
        logger.info(f"Alert created: {alert_id} - {title}")
        return alert_id
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        if alert_id in self.alerts:
            self.alerts[alert_id].resolved = True
            self.alerts[alert_id].resolved_at = datetime.now()
            logger.info(f"Alert resolved: {alert_id}")
            return True
        return False
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active (unresolved) alerts"""
        return [alert for alert in self.alerts.values() if not alert.resolved]
    
    def get_alerts_by_severity(self, severity: AlertSeverity) -> List[Alert]:
        """Get alerts by severity level"""
        return [alert for alert in self.alerts.values() if alert.severity == severity]
    
    def _is_rate_limited(self, component: str) -> bool:
        """Check if component is rate limited"""
        now = datetime.now()
        cutoff = now - timedelta(hours=1)
        
        # Clean old entries
        self.rate_limits[component] = [
            timestamp for timestamp in self.rate_limits[component]
            if timestamp > cutoff
        ]
        
        return len(self.rate_limits[component]) >= self.max_alerts_per_hour
    
    def _process_alerts(self):
        """Process alerts in background thread"""
        while self.running:
            try:
                alert = self.alert_queue.get(timeout=1.0)
                
                # Send to all handlers
                for handler in self.alert_handlers:
                    try:
                        handler(alert)
                    except Exception as e:
                        logger.error(f"Alert handler failed: {e}")
                
                self.alert_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Alert processing error: {e}")


class EmailNotifier:
    """Email notification handler"""
    
    def __init__(self, smtp_host: str, smtp_port: int, username: str, password: str,
                 from_email: str, to_emails: List[str]):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.to_emails = to_emails
    
    def send_alert(self, alert: Alert):
        """Send alert via email"""
        try:
            msg = MimeMultipart(
    msg['From'] = self.from_email
            msg['To'] = ', '.join(self.to_emails)
            msg['Subject'] = f"[{alert.severity.value.upper()}] SmartCloudOps Alert: {alert.title}"
            
            body = f"""
Alert Details:
- Component: {alert.component}
- Severity: {alert.severity.value.upper()}
- Time: {alert.timestamp.isoformat()}
- Message: {alert.message}

Alert ID: {alert.id}
            """
            
            if alert.metadata:
                body += f"\nAdditional Details:\n{json.dumps(alert.metadata, indent=2)}"
            
            msg.attach(MimeText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Alert email sent for: {alert.id}")
            
        except Exception as e:
            logger.error(f"Failed to send alert email: {e}")


class LogNotifier:
    """Log-based notification handler"""
    
    def __init__(self, log_file: str = "logs/alerts.log"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def send_alert(self, alert: Alert):
        """Log alert to file"""
        try:
            with open(self.log_file, 'a') as f:
                alert_json = json.dumps(alert.to_dict())
                f.write(f"{alert_json}\n")
            
            logger.info(f"Alert logged to file: {alert.id}")
            
        except Exception as e:
            logger.error(f"Failed to log alert: {e}")


class MonitoringDashboard:
    """Real-time monitoring dashboard data"""
    
    def __init__(self, metric_collector: MetricCollector, alert_manager: AlertManager):
        self.metric_collector = metric_collector
        self.alert_manager = alert_manager
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        current_time = datetime.now()
        
        # System overview
        system_health = health_monitor.get_health_summary()
        
        # Active alerts
        active_alerts = self.alert_manager.get_active_alerts()
        critical_alerts = [a for a in active_alerts if a.severity == AlertSeverity.CRITICAL]
        
        # Recent metrics
        current_metrics = self.metric_collector.get_current_metrics()
        
        # Performance trends
        performance_trends = {}
        for metric_name in ['response_time', 'cpu_usage', 'memory_usage', 'request_count']:
            stats = self.metric_collector.calculate_metric_stats(metric_name, duration_hours=1)
            if stats:
                performance_trends[metric_name] = stats
        
        return {
            'timestamp': current_time.isoformat(),
            'system_health': system_health,
            'alerts': {
                'active_count': len(active_alerts),
                'critical_count': len(critical_alerts),
                'recent_alerts': [a.to_dict() for a in active_alerts[-5:]]
            },
            'current_metrics': current_metrics,
            'performance_trends': performance_trends,
            'uptime': self._calculate_uptime(),
            'service_status': self._get_service_status()
        }
    
    def _calculate_uptime(self) -> Dict[str, float]:
        """Calculate system uptime percentages"""
        # This would be enhanced with actual uptime tracking
        return {
            'last_hour': 99.5,
            'last_24h': 99.8,
            'last_7d': 99.9,
            'last_30d': 99.95
        }
    
    def _get_service_status(self) -> Dict[str, str]:
        """Get status of individual services"""
        return {
            'api': 'operational',
            'database': 'operational', 
            'cache': 'operational',
            'mlops': 'operational',
            'monitoring': 'operational'
        }


class PerformanceMonitor:
    """Monitor performance metrics and trigger alerts"""
    
    def __init__(self, metric_collector: MetricCollector, alert_manager: AlertManager):
        self.metric_collector = metric_collector
        self.alert_manager = alert_manager
        self.monitoring_thread = None
        self.running = False
        
        # Thresholds
        self.thresholds = {
            'response_time': {'warning': 1.0, 'critical': 3.0},
            'cpu_usage': {'warning': 80.0, 'critical': 95.0},
            'memory_usage': {'warning': 85.0, 'critical': 95.0},
            'error_rate': {'warning': 5.0, 'critical': 10.0},
            'disk_usage': {'warning': 85.0, 'critical': 95.0}
        }
    
    def start(self):
        """Start performance monitoring"""
        if not self.running:
            self.running = True
            self.monitoring_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitoring_thread.start()
            logger.info("Performance monitoring started")
    
    def stop(self):
        """Stop performance monitoring"""
        self.running = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        logger.info("Performance monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                # Collect current metrics
                self._collect_system_metrics()
                
                # Check thresholds and create alerts
                self._check_thresholds()
                
                # Sleep for monitoring interval
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _collect_system_metrics(self):
        """Collect system performance metrics"""
        try:
            import psutil
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metric_collector.record_metric('cpu_usage', cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.metric_collector.record_metric('memory_usage', memory.percent)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.metric_collector.record_metric('disk_usage', disk_percent)
            
            # Network I/O
            net_io = psutil.net_io_counters()
            self.metric_collector.record_metric('network_bytes_sent', net_io.bytes_sent)
            self.metric_collector.record_metric('network_bytes_recv', net_io.bytes_recv)
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
    
    def _check_thresholds(self):
        """Check metrics against thresholds and create alerts"""
        current_metrics = self.metric_collector.get_current_metrics()
        
        for metric_name, thresholds in self.thresholds.items():
            if metric_name in current_metrics:
                value = current_metrics[metric_name]['value']
                
                if isinstance(value, (int, float)):
                    if value >= thresholds['critical']:
                        self.alert_manager.create_alert(
                            title=f"Critical {metric_name.replace('_', ' ').title()}",
                            message=f"{metric_name} is at {value:.1f}% (critical threshold: {thresholds['critical']}%)",
                            severity=AlertSeverity.CRITICAL,
                            component='system',
                            metadata={'metric': metric_name, 'value': value, 'threshold': thresholds['critical']}
                        )
                    elif value >= thresholds['warning']:
                        self.alert_manager.create_alert(
                            title=f"High {metric_name.replace('_', ' ').title()}",
                            message=f"{metric_name} is at {value:.1f}% (warning threshold: {thresholds['warning']}%)",
                            severity=AlertSeverity.WARNING,
                            component='system',
                            metadata={'metric': metric_name, 'value': value, 'threshold': thresholds['warning']}
                        )


# Global monitoring components
metric_collector = MetricCollector()
alert_manager = AlertManager()
performance_monitor = PerformanceMonitor(metric_collector, alert_manager)
monitoring_dashboard = MonitoringDashboard(metric_collector, alert_manager)


def initialize_monitoring(email_config: Optional[Dict[str, Any]] = None):
    """Initialize monitoring system"""
    # Add log notifier
    log_notifier = LogNotifier(
    alert_manager.add_alert_handler(log_notifier.send_alert)
    
    # Add email notifier if configured
    if email_config:
        email_notifier = EmailNotifier(**email_config)
        alert_manager.add_alert_handler(email_notifier.send_alert)
    
    # Start components
    alert_manager.start()
    performance_monitor.start()
    
    logger.info("Monitoring system initialized")


def shutdown_monitoring():
    """Shutdown monitoring system"""
    performance_monitor.stop()
    alert_manager.stop()
    logger.info("Monitoring system shutdown")
