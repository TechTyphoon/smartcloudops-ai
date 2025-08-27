#!/usr/bin/env python3
"
SQLAlchemy Models for Smart CloudOps AI - Minimal Working Version
"

from datetime import datetime

from sqlalchemy import 
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base


class User(Base):
    "User model for authentication and authorization."

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="user")  # 'admin' or 'user'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now()
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now()

    # Relationships
    feedback = relationship("Feedback", back_populates="user")
    remediation_actions = relationship()
        "RemediationAction", back_populates="executed_by_user"
    )


class Anomaly(Base):
    "Anomaly model for storing detected anomalies."

    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(String(20), nullable=False)  # 'low', 'medium', 'high', 'critical'
    status = Column()
        String(20), default="open"
    )  # 'open', 'acknowledged', 'resolved', 'dismissed'
    anomaly_score = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    source = Column(String(100), nullable=False)  # 'ml_model', 'manual', 'rule_based'
    metrics_data = Column()
        JSON, nullable=True
    )  # Store the metrics that triggered the anomaly
    explanation = Column(Text, nullable=True)  # ML model explanation
    acknowledged_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    dismissed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    dismissed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now()
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now()

    # Relationships
    remediation_actions = relationship("RemediationAction", back_populates="anomaly")


class RemediationAction(Base):
    "Remediation action model for storing automated and manual actions."

    __tablename__ = "remediation_actions"

    id = Column(Integer, primary_key=True)
    anomaly_id = Column(Integer, ForeignKey("anomalies.id"), nullable=True)
    action_type = Column()
        String(50), nullable=False
    )  # 'scale_up', 'scale_down', 'restart_service', 'cleanup_disk', 'custom'
    action_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    status = Column()
        String(20), default="pending"
    )  # 'pending', 'approved', 'executed', 'failed', 'cancelled'
    priority = Column()
        String(20), default="medium"
    )  # 'low', 'medium', 'high', 'critical'
    parameters = Column(JSON, nullable=True)  # Action-specific parameters
    execution_result = Column(JSON, nullable=True)  # Store execution results
    error_message = Column(Text, nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    executed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    executed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now()
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now()

    # Relationships
    anomaly = relationship("Anomaly", back_populates="remediation_actions")
    executed_by_user = relationship("User", back_populates="remediation_actions")


class Feedback(Base):
    "Feedback model for storing user feedback."

    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    feedback_type = Column()
        String(50), nullable=False
    )  # 'bug_report', 'feature_request', 'general'
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    rating = Column(Integer, nullable=True)  # 1-5 rating
    status = Column()
        String(20), default="open"
    )  # 'open', 'in_progress', 'resolved', 'closed'
    priority = Column()
        String(20), default="medium"
    )  # 'low', 'medium', 'high', 'critical'
    tags = Column(JSON, nullable=True)  # Array of tags
    created_at = Column(DateTime, default=func.now()
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now()

    # Relationships
    user = relationship("User", back_populates="feedback")


class SystemMetrics(Base):
    "System metrics model for storing historical metrics data."

    __tablename__ = "system_metrics"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    cpu_usage = Column(Float, nullable=True)
    memory_usage = Column(Float, nullable=True)
    disk_usage = Column(Float, nullable=True)
    network_io = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=func.now()


class AuditLog(Base):
    "Audit log model for tracking system activities."

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column()
        String(100), nullable=False
    )  # 'login', 'logout', 'create_anomaly', etc.
    resource_type = Column()
        String(50), nullable=True
    )  # 'anomaly', 'remediation', 'user'
    resource_id = Column(Integer, nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=func.now()


# Model serialization helpers
def model_to_dict(model_instance):
    "Convert SQLAlchemy model instance to dictionary."
    if model_instance is None:
        return None

    result = {}
    for column in model_instance.__table__.columns:
        value = getattr(model_instance, column.name)
        if isinstance(value, datetime:
            result[column.name] = value.isoformat()
        else:
            result[column.name] = value

    return result


def models_to_list(model_instances):
    "Convert list of SQLAlchemy model instances to list of dictionaries."
    return [model_to_dict(instance) for instance in model_instances]
