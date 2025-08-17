# database_integration.py - Production Database Integration Layer
# Smart CloudOps AI Database Service Layer

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from database_config import db
from models import (
    AnomalyDetection,
    ChatOpsInteraction,
    HealthCheck,
    MLTrainingData,
    SecurityScan,
    SystemMetrics,
)
from sqlalchemy import desc, func
from sqlalchemy.exc import SQLAlchemyError


class DatabaseService:
    """Production database service layer"""

    def __init__(self):
        self.session = db.session

    # System Metrics Operations
    def store_system_metrics(self, metrics_data: Dict[str, Any]) -> Optional[int]:
        """Store real-time system metrics"""
        try:
            metrics = SystemMetrics(
                cpu_usage_percent=metrics_data.get("cpu_usage_percent", 0),
                cpu_count=metrics_data.get("cpu_count", 0),
                load_avg_1min=metrics_data.get("load_avg_1min", 0),
                load_avg_5min=metrics_data.get("load_avg_5min", 0),
                load_avg_15min=metrics_data.get("load_avg_15min", 0),
                memory_total_gb=metrics_data.get("memory_total_gb", 0),
                memory_used_gb=metrics_data.get("memory_used_gb", 0),
                memory_available_gb=metrics_data.get("memory_available_gb", 0),
                memory_usage_percent=metrics_data.get("memory_usage_percent", 0),
                disk_total_gb=metrics_data.get("disk_total_gb", 0),
                disk_used_gb=metrics_data.get("disk_used_gb", 0),
                disk_free_gb=metrics_data.get("disk_free_gb", 0),
                disk_usage_percent=metrics_data.get("disk_usage_percent", 0),
                network_bytes_sent=metrics_data.get("network_bytes_sent", 0),
                network_bytes_recv=metrics_data.get("network_bytes_recv", 0),
                network_packets_sent=metrics_data.get("network_packets_sent", 0),
                network_packets_recv=metrics_data.get("network_packets_recv", 0),
                process_count=metrics_data.get("process_count", 0),
                uptime_seconds=metrics_data.get("uptime_seconds", 0),
            )

            self.session.add(metrics)
            self.session.commit()
            return metrics.id

        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Error storing system metrics: {e}")
            return None

    def get_recent_metrics(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent system metrics"""
        try:
            since = datetime.utcnow() - timedelta(hours=hours)
            metrics = (
                self.session.query(SystemMetrics)
                .filter(SystemMetrics.timestamp >= since)
                .order_by(desc(SystemMetrics.timestamp))
                .limit(1000)
                .all()
            )
            return [metric.to_dict() for metric in metrics]
        except SQLAlchemyError as e:
            print(f"Error retrieving metrics: {e}")
            return []

    def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get metrics summary statistics"""
        try:
            since = datetime.utcnow() - timedelta(hours=hours)
            result = (
                self.session.query(
                    func.avg(SystemMetrics.cpu_usage_percent).label("avg_cpu"),
                    func.max(SystemMetrics.cpu_usage_percent).label("max_cpu"),
                    func.avg(SystemMetrics.memory_usage_percent).label("avg_memory"),
                    func.max(SystemMetrics.memory_usage_percent).label("max_memory"),
                    func.avg(SystemMetrics.disk_usage_percent).label("avg_disk"),
                    func.count().label("sample_count"),
                )
                .filter(SystemMetrics.timestamp >= since)
                .first()
            )

            if result:
                return {
                    "period_hours": hours,
                    "sample_count": result.sample_count or 0,
                    "cpu_stats": {
                        "average_percent": round(result.avg_cpu or 0, 2),
                        "peak_percent": round(result.max_cpu or 0, 2),
                    },
                    "memory_stats": {
                        "average_percent": round(result.avg_memory or 0, 2),
                        "peak_percent": round(result.max_memory or 0, 2),
                    },
                    "disk_stats": {"average_percent": round(result.avg_disk or 0, 2)},
                }
            return {}
        except SQLAlchemyError as e:
            print(f"Error getting metrics summary: {e}")
            return {}

    # ML Training Data Operations
    def store_training_data(self, training_records: List[Dict[str, Any]]) -> int:
        """Store ML training data records"""
        try:
            stored_count = 0
            for record in training_records:
                ml_data = MLTrainingData(
                    cpu_usage=record.get("cpu_usage", 0),
                    memory_usage=record.get("memory_usage", 0),
                    disk_usage=record.get("disk_usage", 0),
                    network_traffic=record.get("network_traffic", 0),
                    process_count=record.get("process_count", 0),
                    anomaly_label=record.get("anomaly_label", "normal"),
                    severity_score=record.get("severity_score", 0.0),
                    category=record.get("category", "system_monitoring"),
                    source=record.get("source", "real_system_data"),
                    validated=record.get("validated", True),
                )
                self.session.add(ml_data)
                stored_count += 1

            self.session.commit()
            return stored_count
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Error storing training data: {e}")
            return 0

    def get_training_data_stats(self) -> Dict[str, Any]:
        """Get ML training data statistics"""
        try:
            total_records = self.session.query(MLTrainingData).count()
            anomaly_counts = (
                self.session.query(
                    MLTrainingData.anomaly_label, func.count().label("count")
                )
                .group_by(MLTrainingData.anomaly_label)
                .all()
            )

            return {
                "total_records": total_records,
                "anomaly_distribution": {
                    label: count for label, count in anomaly_counts
                },
                "data_source": "real_system_data",
                "last_updated": datetime.utcnow().isoformat(),
            }
        except SQLAlchemyError as e:
            print(f"Error getting training data stats: {e}")
            return {"total_records": 0}

    # Anomaly Detection Operations
    def store_anomaly_detection(self, anomaly_data: Dict[str, Any]) -> Optional[int]:
        """Store anomaly detection result"""
        try:
            anomaly = AnomalyDetection(
                anomaly_type=anomaly_data.get("anomaly_type", "unknown"),
                severity=anomaly_data.get("severity", "low"),
                confidence_score=anomaly_data.get("confidence_score", 0.0),
                description=anomaly_data.get("description", ""),
                affected_components=anomaly_data.get("affected_components", []),
                recommended_actions=anomaly_data.get("recommended_actions", []),
                status="detected",
            )

            self.session.add(anomaly)
            self.session.commit()
            return anomaly.id
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Error storing anomaly detection: {e}")
            return None

    def get_active_anomalies(self) -> List[Dict[str, Any]]:
        """Get active (unresolved) anomalies"""
        try:
            anomalies = (
                self.session.query(AnomalyDetection)
                .filter(AnomalyDetection.status.in_(["detected", "investigating"]))
                .order_by(desc(AnomalyDetection.timestamp))
                .all()
            )
            return [anomaly.to_dict() for anomaly in anomalies]
        except SQLAlchemyError as e:
            print(f"Error getting active anomalies: {e}")
            return []

    # Health Check Operations
    def store_health_check(self, check_data: Dict[str, Any]) -> Optional[int]:
        """Store health check result"""
        try:
            health_check = HealthCheck(
                check_type=check_data.get("check_type", "unknown"),
                component=check_data.get("component", "unknown"),
                status=check_data.get("status", "unknown"),
                response_time_ms=check_data.get("response_time_ms", 0),
                message=check_data.get("message", ""),
                details=check_data.get("details", {}),
                error_details=check_data.get("error_details", None),
            )

            self.session.add(health_check)
            self.session.commit()
            return health_check.id
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Error storing health check: {e}")
            return None

    def get_health_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get health check summary"""
        try:
            since = datetime.utcnow() - timedelta(hours=hours)

            # Get latest health check for each component
            latest_checks = (
                self.session.query(HealthCheck)
                .filter(HealthCheck.timestamp >= since)
                .order_by(desc(HealthCheck.timestamp))
                .all()
            )

            # Group by component and get latest
            component_health = {}
            for check in latest_checks:
                if check.component not in component_health:
                    component_health[check.component] = check.to_dict()

            # Count status distribution
            status_counts = (
                self.session.query(HealthCheck.status, func.count().label("count"))
                .filter(HealthCheck.timestamp >= since)
                .group_by(HealthCheck.status)
                .all()
            )

            return {
                "period_hours": hours,
                "components": component_health,
                "status_distribution": {
                    status: count for status, count in status_counts
                },
                "total_checks": len(latest_checks),
                "last_updated": datetime.utcnow().isoformat(),
            }
        except SQLAlchemyError as e:
            print(f"Error getting health summary: {e}")
            return {}

    # ChatOps Operations
    def store_chatops_interaction(
        self, interaction_data: Dict[str, Any]
    ) -> Optional[int]:
        """Store ChatOps interaction"""
        try:
            interaction = ChatOpsInteraction(
                user_query=interaction_data.get("user_query", ""),
                intent=interaction_data.get("intent", "unknown"),
                analysis_result=interaction_data.get("analysis_result", {}),
                recommendations=interaction_data.get("recommendations", []),
                system_context=interaction_data.get("system_context", {}),
                response_generated=interaction_data.get("response_generated", ""),
                processing_time_ms=interaction_data.get("processing_time_ms", 0),
                confidence_score=interaction_data.get("confidence_score", 0.0),
            )

            self.session.add(interaction)
            self.session.commit()
            return interaction.id
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Error storing ChatOps interaction: {e}")
            return None

    def get_chatops_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get ChatOps interaction history"""
        try:
            interactions = (
                self.session.query(ChatOpsInteraction)
                .order_by(desc(ChatOpsInteraction.timestamp))
                .limit(limit)
                .all()
            )
            return [interaction.to_dict() for interaction in interactions]
        except SQLAlchemyError as e:
            print(f"Error getting ChatOps history: {e}")
            return []

    # Security Scan Operations
    def store_security_scan(self, scan_data: Dict[str, Any]) -> Optional[int]:
        """Store security scan results"""
        try:
            scan = SecurityScan(
                scan_type=scan_data.get("scan_type", "unknown"),
                target=scan_data.get("target", ""),
                total_issues=scan_data.get("total_issues", 0),
                high_severity=scan_data.get("high_severity", 0),
                medium_severity=scan_data.get("medium_severity", 0),
                low_severity=scan_data.get("low_severity", 0),
                issues=scan_data.get("issues", []),
                scan_duration_seconds=scan_data.get("scan_duration_seconds", 0),
            )

            self.session.add(scan)
            self.session.commit()
            return scan.id
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Error storing security scan: {e}")
            return None

    def get_latest_security_status(self) -> Dict[str, Any]:
        """Get latest security scan status"""
        try:
            latest_scan = (
                self.session.query(SecurityScan)
                .order_by(desc(SecurityScan.timestamp))
                .first()
            )

            if latest_scan:
                return latest_scan.to_dict()
            return {}
        except SQLAlchemyError as e:
            print(f"Error getting security status: {e}")
            return {}

    # Database Maintenance
    def cleanup_old_data(self, days: int = 30) -> Dict[str, int]:
        """Clean up old data to maintain performance"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            # Keep only recent data for performance
            deleted_metrics = (
                self.session.query(SystemMetrics)
                .filter(SystemMetrics.timestamp < cutoff_date)
                .count()
            )

            if deleted_metrics > 0:
                (
                    self.session.query(SystemMetrics)
                    .filter(SystemMetrics.timestamp < cutoff_date)
                    .delete()
                )

            # Clean up old health checks
            deleted_health = (
                self.session.query(HealthCheck)
                .filter(HealthCheck.timestamp < cutoff_date)
                .count()
            )

            if deleted_health > 0:
                (
                    self.session.query(HealthCheck)
                    .filter(HealthCheck.timestamp < cutoff_date)
                    .delete()
                )

            self.session.commit()

            return {
                "deleted_metrics": deleted_metrics,
                "deleted_health_checks": deleted_health,
                "cutoff_days": days,
            }
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Error during cleanup: {e}")
            return {}


# Global database service instance
db_service = DatabaseService()


def get_db_connection():
    """Get database connection for health checks"""
    try:
        # Test the database connection
        db_service.session.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
