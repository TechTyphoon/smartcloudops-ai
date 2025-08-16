# models.py - Production Database Models
# Smart CloudOps AI Data Models

from datetime import datetime

from database_config import db
from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


# Base Model with common fields
class BaseModel(db.Model):
    """Base model with common timestamp fields"""

    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self):
        """Convert model instance to dictionary"""
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }


# System Metrics Model
class SystemMetrics(BaseModel):
    """Store real-time system metrics"""

    __tablename__ = "system_metrics"

    timestamp = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, index=True
    )

    # CPU Metrics
    cpu_usage_percent = db.Column(db.Float, nullable=False)
    cpu_count = db.Column(db.Integer, nullable=False)
    load_avg_1min = db.Column(db.Float, nullable=False)
    load_avg_5min = db.Column(db.Float, nullable=False)
    load_avg_15min = db.Column(db.Float, nullable=False)

    # Memory Metrics
    memory_total_gb = db.Column(db.Float, nullable=False)
    memory_used_gb = db.Column(db.Float, nullable=False)
    memory_available_gb = db.Column(db.Float, nullable=False)
    memory_usage_percent = db.Column(db.Float, nullable=False)

    # Disk Metrics
    disk_total_gb = db.Column(db.Float, nullable=False)
    disk_used_gb = db.Column(db.Float, nullable=False)
    disk_free_gb = db.Column(db.Float, nullable=False)
    disk_usage_percent = db.Column(db.Float, nullable=False)

    # Network Metrics
    network_bytes_sent = db.Column(db.Integer, nullable=False, default=0)
    network_bytes_recv = db.Column(db.Integer, nullable=False, default=0)
    network_packets_sent = db.Column(db.Integer, nullable=False, default=0)
    network_packets_recv = db.Column(db.Integer, nullable=False, default=0)

    # System Info
    process_count = db.Column(db.Integer, nullable=False)
    uptime_seconds = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<SystemMetrics {self.timestamp}: CPU={self.cpu_usage_percent}%, Memory={self.memory_usage_percent}%>"


# ML Training Data Model
class MLTrainingData(BaseModel):
    """Store ML training data records"""

    __tablename__ = "ml_training_data"

    # Data characteristics
    cpu_usage = db.Column(db.Float, nullable=False)
    memory_usage = db.Column(db.Float, nullable=False)
    disk_usage = db.Column(db.Float, nullable=False)
    network_traffic = db.Column(db.Float, nullable=False, default=0.0)
    process_count = db.Column(db.Integer, nullable=False, default=0)

    # Labels and classifications
    anomaly_label = db.Column(db.String(50), nullable=False, default="normal")
    severity_score = db.Column(db.Float, nullable=False, default=0.0)
    category = db.Column(db.String(100), nullable=False, default="system_monitoring")

    # Metadata
    source = db.Column(db.String(100), nullable=False, default="real_system_data")
    validated = db.Column(db.Boolean, nullable=False, default=True)

    def __repr__(self):
        return (
            f"<MLTrainingData {self.id}: {self.anomaly_label} - CPU={self.cpu_usage}%>"
        )


# Anomaly Detection Results
class AnomalyDetection(BaseModel):
    """Store anomaly detection results"""

    __tablename__ = "anomaly_detections"

    # Detection metadata
    timestamp = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, index=True
    )
    anomaly_type = db.Column(db.String(100), nullable=False)
    severity = db.Column(db.String(20), nullable=False)  # low, medium, high, critical
    confidence_score = db.Column(db.Float, nullable=False)

    # System state at detection
    system_metrics_id = db.Column(
        db.Integer, db.ForeignKey("system_metrics.id"), nullable=True
    )
    system_metrics = relationship("SystemMetrics", backref="anomalies")

    # Detection details
    description = db.Column(db.Text, nullable=False)
    affected_components = db.Column(
        db.JSON, nullable=True
    )  # Store list of affected system components
    recommended_actions = db.Column(
        db.JSON, nullable=True
    )  # Store list of recommended remediation actions

    # Status tracking
    status = db.Column(
        db.String(50), nullable=False, default="detected"
    )  # detected, investigating, resolved, false_positive
    resolved_at = db.Column(db.DateTime, nullable=True)
    resolution_notes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<AnomalyDetection {self.id}: {self.anomaly_type} - {self.severity}>"


# Remediation Actions
class RemediationAction(BaseModel):
    """Store automated remediation actions"""

    __tablename__ = "remediation_actions"

    # Action metadata
    anomaly_id = db.Column(
        db.Integer, db.ForeignKey("anomaly_detections.id"), nullable=False
    )
    anomaly = relationship("AnomalyDetection", backref="remediation_actions")

    # Action details
    action_type = db.Column(
        db.String(100), nullable=False
    )  # restart_service, clear_cache, scale_resources, etc.
    action_description = db.Column(db.Text, nullable=False)
    execution_command = db.Column(db.Text, nullable=True)

    # Execution tracking
    status = db.Column(
        db.String(50), nullable=False, default="pending"
    )  # pending, running, completed, failed
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    execution_log = db.Column(db.Text, nullable=True)

    # Results
    success = db.Column(db.Boolean, nullable=True)
    result_message = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<RemediationAction {self.id}: {self.action_type} - {self.status}>"


# ChatOps History
class ChatOpsInteraction(BaseModel):
    """Store ChatOps interactions and analysis"""

    __tablename__ = "chatops_interactions"

    # Interaction metadata
    timestamp = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, index=True
    )
    user_query = db.Column(db.Text, nullable=False)
    intent = db.Column(db.String(100), nullable=False)

    # Analysis results
    analysis_result = db.Column(
        db.JSON, nullable=False
    )  # Store complex analysis results
    recommendations = db.Column(db.JSON, nullable=True)  # Store AI recommendations

    # Context information
    system_context = db.Column(db.JSON, nullable=True)  # System state at time of query
    response_generated = db.Column(db.Text, nullable=False)
    processing_time_ms = db.Column(db.Integer, nullable=False, default=0)

    # Quality metrics
    confidence_score = db.Column(db.Float, nullable=False, default=0.0)
    user_feedback = db.Column(
        db.String(20), nullable=True
    )  # helpful, not_helpful, etc.

    def __repr__(self):
        return (
            f"<ChatOpsInteraction {self.id}: {self.intent} - {self.confidence_score}>"
        )


# Application Health Monitoring
class HealthCheck(BaseModel):
    """Store application health check results"""

    __tablename__ = "health_checks"

    # Check metadata
    timestamp = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, index=True
    )
    check_type = db.Column(
        db.String(50), nullable=False
    )  # database, api, system, external
    component = db.Column(db.String(100), nullable=False)

    # Health status
    status = db.Column(db.String(20), nullable=False)  # healthy, degraded, unhealthy
    response_time_ms = db.Column(db.Integer, nullable=False, default=0)

    # Details
    message = db.Column(db.Text, nullable=True)
    details = db.Column(db.JSON, nullable=True)  # Additional health check details
    error_details = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<HealthCheck {self.timestamp}: {self.component} - {self.status}>"


# Security Scan Results
class SecurityScan(BaseModel):
    """Store security scan results"""

    __tablename__ = "security_scans"

    # Scan metadata
    timestamp = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, index=True
    )
    scan_type = db.Column(
        db.String(50), nullable=False
    )  # bandit, dependency, configuration
    target = db.Column(db.String(200), nullable=False)

    # Scan results
    total_issues = db.Column(db.Integer, nullable=False, default=0)
    high_severity = db.Column(db.Integer, nullable=False, default=0)
    medium_severity = db.Column(db.Integer, nullable=False, default=0)
    low_severity = db.Column(db.Integer, nullable=False, default=0)

    # Detailed results
    issues = db.Column(db.JSON, nullable=True)  # Store detailed issue information
    scan_duration_seconds = db.Column(db.Integer, nullable=False, default=0)

    # Status
    status = db.Column(db.String(20), nullable=False, default="completed")

    def __repr__(self):
        return (
            f"<SecurityScan {self.id}: {self.scan_type} - {self.total_issues} issues>"
        )


# Model registry for easy access
MODEL_REGISTRY = {
    "SystemMetrics": SystemMetrics,
    "MLTrainingData": MLTrainingData,
    "AnomalyDetection": AnomalyDetection,
    "RemediationAction": RemediationAction,
    "ChatOpsInteraction": ChatOpsInteraction,
    "HealthCheck": HealthCheck,
    "SecurityScan": SecurityScan,
}
