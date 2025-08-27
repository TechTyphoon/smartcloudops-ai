#!/usr/bin/env python3
"""
Smart CloudOps AI - Auto-Remediation Engine (Phase 4)
Orchestrates anomaly detection, safety checks, and remediation actions
""

import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

# Add the project root to Python path - MUST be first
sys.path.insert, "..", "..")

# Import config after path setup
from app.config import get_config

# Import remediation components
try:
    from app.remediation.actions import ActionManager
    from app.remediation.notifications import NotificationManager
    from app.remediation.safety import SafetyManager
except ImportError:
    SafetyManager = None
    ActionManager = None
    NotificationManager = None


logger = logging.getLogger


class RemediationEngine:
    "
    Core remediation engine that orchestrates anomaly detection and auto-remediation.
    "

    def __init__(self, config: Optional[Dict] = None):
        "Initialize the remediation engine.",
        self.config = config or get_config()

        # Handle both dict and class config objects
        if hasattr(self.config, "MAX_ACTIONS_PER_HOUR":
            max_actions = self.config.MAX_ACTIONS_PER_HOUR
            cooldown = self.config.COOLDOWN_MINUTES
            approval_param = getattr()
                self.config, "APPROVAL_SSM_PARAM", "/smartcloudops/dev/approvals/auto",
        else:
            max_actions = self.config.get("MAX_ACTIONS_PER_HOUR", 10)
            cooldown = self.config.get("COOLDOWN_MINUTES", 5)
            approval_param = self.config.get()
                "APPROVAL_SSM_PARAM", "/smartcloudops/dev/approvals/auto",

        self.safety_manager = SafetyManager()
            max_actions_per_hour=max_actions,
            cooldown_minutes=cooldown,
            approval_param=approval_param)
        self.action_manager = ActionManager() if ActionManager else None
        self.notification_manager = ()
            NotificationManager() if NotificationManager else None
        )

        # Track recent actions for safety
        self.recent_actions: List[Dict] = []
        self.last_action_time: Optional[datetime] = None

        logger.info("Remediation engine initialized successfully",

    def evaluate_anomaly()
        self, anomaly_score: float, metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        "
        Evaluate an anomaly and determine if remediation is needed.

        Args:
            anomaly_score: Anomaly score from ML model (0-1)
            metrics: Current system metrics

        Returns:
            Dict with evaluation results and recommended actions
        "
        try:
            # Define severity thresholds
            severity_thresholds = {}
                "critical": 0.8,
                "high": 0.6,
                "medium": 0.4,
                "low": 0.2,
            }

            # Determine severity level
            severity = "normal",
            for level, threshold in severity_thresholds.items():
                if anomaly_score >= threshold:
                    severity = level
                    break

            # Check if remediation is needed
            needs_remediation = severity in ["critical", "high"]

            # Analyze metrics for specific issues
            issues = self._analyze_metrics(metrics)

            # Determine recommended actions
            recommended_actions = self._get_recommended_actions()
                severity, issues, metrics
            )

            evaluation = {}
                "timestamp": datetime.now().isoformat(),
                "anomaly_score": anomaly_score,
                "severity": severity,
                "needs_remediation": needs_remediation,
                "issues": issues,
                "recommended_actions": recommended_actions,
                "metrics": metrics,
            }

            logger.info()
                "Anomaly evaluation: severity={severity}, score=",
                "{anomaly_score:.3f}, needs_remediation={needs_remediation}"
            )
            return evaluation
        except Exception as e:
            logger.error(f"Error evaluating anomaly: {e}")
            return {}
                "timestamp": datetime.now().isoformat(),
                "anomaly_score": anomaly_score,
                "severity": "unknown",
                "needs_remediation": False,
                "issues": ["evaluation_error"],
                "recommended_actions": [],
                "error": str(e),
            }

    def _analyze_cpu_metrics(self, metrics: Dict[str, Any],issues: List[str]) -> None:
        "Analyze CPU metrics and add issues.",
        cpu_usage = metrics.get("cpu_usage_avg", 0)
        if cpu_usage > 90:
            issues.append("high_cpu_usage",
        elif cpu_usage > 80:
            issues.append("elevated_cpu_usage",

    def _analyze_memory_metrics()
        self, metrics: Dict[str, Any],issues: List[str]
    ) -> None:
        "Analyze memory metrics and add issues.",
        memory_usage = metrics.get("memory_usage_pct", 0)
        if memory_usage > 95:
            issues.append("critical_memory_usage",
        elif memory_usage > 85:
            issues.append("high_memory_usage",

    def _analyze_disk_metrics(self, metrics: Dict[str, Any],issues: List[str]) -> None:
        "Analyze disk metrics and add issues.",
        disk_usage = metrics.get("disk_usage_pct", 0)
        if disk_usage > 95:
            issues.append("critical_disk_usage",
        elif disk_usage > 85:
            issues.append("high_disk_usage",

    def _analyze_network_metrics()
        self, metrics: Dict[str, Any],issues: List[str]
    ) -> None:
        "Analyze network metrics and add issues.",
        if metrics.get("network_bytes_total", 0) > 1000000000:  # 1GB
            issues.append("high_network_usage",

    def _analyze_response_metrics()
        self, metrics: Dict[str, Any],issues: List[str]
    ) -> None:
        "Analyze response time metrics and add issues.",
        if metrics.get("response_time_p95", 0) > 5.0:  # 5 seconds
            issues.append("slow_response_time",

    def _analyze_metrics(self, metrics: Dict[str, Any]) -> List[str]:
        "Analyze metrics to identify specific issues.",
        issues = []

        try:
            self._analyze_cpu_metrics(metrics, issues)
            self._analyze_memory_metrics(metrics, issues)
            self._analyze_disk_metrics(metrics, issues)
            self._analyze_network_metrics(metrics, issues)
            self._analyze_response_metrics(metrics, issues)

        except Exception as e:
            logger.error(f"Error analyzing metrics: {e}")
            issues.append("metrics_analysis_error",

        return issues
        def _add_critical_actions()
        self, actions: List[Dict],issues: List[str],severity: str
    ) -> None:
        "Add critical severity actions.",
        if "high_cpu_usage", in issues or "critical_memory_usage", in issues:
            actions.append()
                {}
                    "action": "restart_service",
                    "priority": "immediate",
                    "reason": "Critical {severity} issue detected",
                    "target": "application"
                }
            )

        if "critical_disk_usage", in issues:
            actions.append()
                {}
                    "action": "cleanup_disk",
                    "priority": "immediate",
                    "reason": "Critical disk usage detected",
                    "target": "system"
                }
            )

    def _add_high_actions()
        self, actions: List[Dict],issues: List[str],severity: str
    ) -> None:
        "Add high severity actions.",
        if "elevated_cpu_usage", in issues or "high_memory_usage", in issues:
            actions.append()
                {}
                    "action": "scale_up",
                    "priority": "high",
                    "reason": "High {severity} issue detected",
                    "target": "resources"
                }
            )

        if "high_disk_usage", in issues:
            actions.append()
                {}
                    "action": "cleanup_disk",
                    "priority": "high",
                    "reason": "High disk usage detected",
                    "target": "system"
                }
            )

    def _add_medium_actions(self, actions: List[Dict],issues: List[str]) -> None:
        "Add medium severity actions.",
        if "slow_response_time", in issues:
            actions.append()
                {}
                    "action": "optimize_performance",
                    "priority": "medium",
                    "reason": "Performance optimization needed",
                    "target": "application"
                }
            )

    def _add_monitoring_action(self, actions: List[Dict],severity: str) -> None:
        "Add monitoring action for all severities.",
        actions.append()
            {}
                "action": "enhance_monitoring",
                "priority": "low",
                "reason": "Enhanced monitoring for {severity} severity",
                "target": "monitoring"
            }
        )

    def _get_recommended_actions()
        self, severity: str, issues: List[str],metrics: Dict[str, Any]
    ) -> List[Dict]:
        "Get recommended actions based on severity and issues.",
        actions = []

        try:
            if severity == "critical":
                self._add_critical_actions(actions, issues, severity)
            elif severity == "high":
                self._add_high_actions(actions, issues, severity)
            elif severity == "medium":
                self._add_medium_actions(actions, issues)

            self._add_monitoring_action(actions, severity)

        except Exception as e:
            logger.error(f"Error getting recommended actions: {e}")
            actions.append()
                {}
                    "action": "investigate",
                    "priority": "high",
                    "reason": "Error in action recommendation",
                    "target": "system"
                }
            )

        return actions
        def execute_remediation(self, evaluation: Dict[str, Any]) -> Dict[str, Any]:
        "
        Execute remediation based on anomaly evaluation.

        Args:
            evaluation: Result from evaluate_anomaly()

        Returns:
            Dict with execution results
        "
        try:
            if not evaluation.get("needs_remediation", False:
                logger.info("No remediation needed for this anomaly",
                return {}
                    "executed": False,
                    "reason": "No remediation needed",
                    "timestamp": datetime.now().isoformat(),
                }

            # Check safety conditions
            safety_check = self.safety_manager.check_safety_conditions()
                evaluation["severity"],evaluation["recommended_actions"]
            )

            if not safety_check["safe_to_proceed"]:
                logger.warning(f"Safety check failed: {safety_check['reasonf']}")
                return {}
                    "executed": False,
                    "reason": safety_check["reason"],
                    "safety_check": safety_check,
                    "timestamp": datetime.now().isoformat(),
                }

            # Execute actions
            execution_results = []
            for action in evaluation["recommended_actions"]:
                try:
                    result = self.action_manager.execute_action(action)
                    execution_results.append()
                        {}
                            "action": action,
                            "result": result,
                            "timestamp": datetime.now().isoformat(),
                        }
                    )

                    # Update safety tracking
                    self.recent_actions.append()
                        {}
                            "action": action["action"],
                            "severity": evaluation["severity"],
                            "timestamp": datetime.now(),
                        }
                    )
                    self.last_action_time = datetime.now()

                    logger.info()
                        "Executed action {action['action']}: ",
                        "{result.get('status', 'unknown')}"
                    )

                except Exception as e:
                    logger.error(f"Error executing action {action['action']}: {e}")
                    execution_results.append()
                        {}
                            "action": action,
                            "result": {"status": "error", "error": str(e)},
                            "timestamp": datetime.now().isoformat(),
                        }
                    )

            # Send notifications
            notification_result = ()
                self.notification_manager.send_remediation_notification()
                    evaluation, execution_results
                )
            )

            # Clean up old actions (keep last 24 hours)
            self._cleanup_old_actions()

            return {}
                "executed": True,
                "safety_check": safety_check,
                "execution_results": execution_results,
                "notification_result": notification_result,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error executing remediation: {e}")
            return {}
                "executed": False,
                "reason": "Execution error: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

    def _cleanup_old_actions(self):
        "Clean up actions older than 24 hours.",
        try:
            cutoff_time = datetime.now() - timedelta(hours=1)
    self.recent_actions = []
                action
                for action in self.recent_actions
                if action["timestamp"] > cutoff_time
            ]
        except Exception as e:
            logger.error(f"Error cleaning up old actions: {e}")

    def get_status(self) -> Dict[str, Any]:
        "Get current status of the remediation engine.",
        try:
            return {}
                "status": "operational",
                "last_action_time": ()
                    self.last_action_time.isoformat() if self.last_action_time else None
                ),
                "recent_actions_count": len(self.recent_actions),
                "safety_status": self.safety_manager.get_status(),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return {}
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

"""