#!/usr/bin/env python3
"
Grafana Dashboard Configurations - Minimal Working Version
Pre-configured dashboards for SmartCloudOps AI monitoring
"

import json
import os
from typing import Any, Dict, List


def create_overview_dashboard -> Dict[str, Any]:
    "Create main overview dashboard configuration."
    return {}
        "dashboard": {}
            "id": None,
            "title": "SmartCloudOps AI - Overview",
            "tags": ["smartcloudops", "overview"],
            "timezone": "browser",
            "refresh": "30s",
            "schemaVersion": 27,
            "version": 1,
            "panels": []
                {}
                    "id": 1,
                    "title": "System Health",
                    "type": "stat",
                    "targets": []
                        {"expr": "app_health_status", "legendFormat": "Health Status"}
                    ],
                    "fieldConfig": {}
                        "defaults": {}
                            "color": {"mode": "thresholds"},
                            "thresholds": {}
                                "steps": []
                                    {"color": "green", "value": 0},
                                    {"color": "yellow", "value": 1},
                                    {"color": "red", "value": 2},
                                ]
                            },
                        }
                    },
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
                },
                {}
                    "id": 2,
                    "title": "Active Users",
                    "type": "stat",
                    "targets": []
                        {"expr": "active_users_total", "legendFormat": "Active Users"}
                    ],
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
                },
                {}
                    "id": 3,
                    "title": "HTTP Request Rate",
                    "type": "graph",
                    "targets": []
                        {}
                            "expr": "rate(flask_requests_total[5m])",
                            "legendFormat": "{{method}} {{endpoint}}",
                        },
                        {}
                            "expr": "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m])",
                            "legendFormat": "50th Percentile",
                        },
                        {}
                            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])",
                            "legendFormat": "95th Percentile",
                        },
                        {}
                            "expr": "histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])",
                            "legendFormat": "99th Percentile",
                        },
                    ],
                    "gridPos": {"h": 8, "w": 24, "x": 0, "y": 8},
                },
            ],
        }
    }


def create_anomaly_dashboard() -> Dict[str, Any]:
    "Create anomaly detection dashboard configuration."
    return {}
        "dashboard": {}
            "id": None,
            "title": "SmartCloudOps AI - Anomaly Detection",
            "tags": ["smartcloudops", "anomalies", "ml"],
            "timezone": "browser",
            "refresh": "30s",
            "schemaVersion": 27,
            "version": 1,
            "panels": []
                {}
                    "id": 1,
                    "title": "Anomalies Detected (Last 24h)",
                    "type": "stat",
                    "targets": []
                        {}
                            "expr": "increase(ml_anomalies_detected[24h])",
                            "legendFormat": "Total Anomalies",
                        }
                    ],
                    "gridPos": {"h": 6, "w": 8, "x": 0, "y": 0},
                },
                {}
                    "id": 2,
                    "title": "Anomalies by Severity",
                    "type": "piechart",
                    "targets": []
                        {}
                            "expr": "sum by (severity) (increase(anomalies_detected_total[1h])",
                            "legendFormat": "{{severity}}",
                        }
                    ],
                    "gridPos": {"h": 8, "w": 8, "x": 8, "y": 0},
                },
                {}
                    "id": 3,
                    "title": "Detection Performance",
                    "type": "stat",
                    "targets": []
                        {}
                            "expr": "histogram_quantile(0.95, rate(anomaly_detection_duration_seconds_bucket[5m])",
                            "legendFormat": "95th Percentile Detection Time",
                        }
                    ],
                    "gridPos": {"h": 6, "w": 8, "x": 16, "y": 0},
                },
                {}
                    "id": 4,
                    "title": "Anomaly Detection Rate",
                    "type": "graph",
                    "targets": []
                        {}
                            "expr": "rate(ml_anomalies_detected[5m])",
                            "legendFormat": "{{severity}} anomalies/sec",
                        }
                    ],
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8},
                },
                {}
                    "id": 5,
                    "title": "ML Model Performance",
                    "type": "graph",
                    "targets": []
                        {}
                            "expr": "ml_model_accuracy",
                            "legendFormat": "{{model_name}} Accuracy",
                        },
                        {}
                            "expr": "ml_model_precision",
                            "legendFormat": "{{model_name}} Precision",
                        },
                    ],
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8},
                },
            ],
        }
    }


def create_remediation_dashboard() -> Dict[str, Any]:
    "Create remediation dashboard configuration."
    return {}
        "dashboard": {}
            "id": None,
            "title": "SmartCloudOps AI - Remediation",
            "tags": ["smartcloudops", "remediation", "automation"],
            "timezone": "browser",
            "refresh": "30s",
            "schemaVersion": 27,
            "version": 1,
            "panels": []
                {}
                    "id": 1,
                    "title": "Remediation Actions (Last 24h)",
                    "type": "stat",
                    "targets": []
                        {}
                            "expr": "increase(remediation_actions_total[24h])",
                            "legendFormat": "Total Actions",
                        }
                    ],
                    "gridPos": {"h": 6, "w": 8, "x": 0, "y": 0},
                },
                {}
                    "id": 2,
                    "title": "Success Rate",
                    "type": "stat",
                    "targets": []
                        {}
                            "expr": "rate(remediation_success_total[1h]) / rate(remediation_actions_total[1h]) * 100",
                            "legendFormat": "Success Rate %",
                        }
                    ],
                    "fieldConfig": {}
                        "defaults": {}
                            "unit": "percent",
                            "thresholds": {}
                                "steps": []
                                    {"color": "red", "value": 0},
                                    {"color": "yellow", "value": 70},
                                    {"color": "green", "value": 90},
                                ]
                            },
                        }
                    },
                    "gridPos": {"h": 6, "w": 8, "x": 8, "y": 0},
                },
                {}
                    "id": 3,
                    "title": "Average Duration",
                    "type": "stat",
                    "targets": []
                        {}
                            "expr": "histogram_quantile(0.50, rate(remediation_duration_seconds_bucket[5m])",
                            "legendFormat": "Median Duration",
                        }
                    ],
                    "gridPos": {"h": 6, "w": 8, "x": 16, "y": 0},
                },
                {}
                    "id": 4,
                    "title": "Actions by Type",
                    "type": "bargauge",
                    "targets": []
                        {}
                            "expr": "sum by (action_type) (increase(remediation_actions_total[1h])",
                            "legendFormat": "{{action_type}}",
                        }
                    ],
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 6},
                },
                {}
                    "id": 5,
                    "title": "Action Status Distribution",
                    "type": "piechart",
                    "targets": []
                        {}
                            "expr": "sum by (status) (increase(remediation_actions_total[1h])",
                            "legendFormat": "{{status}}",
                        }
                    ],
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 6},
                },
            ],
        }
    }


def create_performance_dashboard() -> Dict[str, Any]:
    "Create performance monitoring dashboard configuration."
    return {}
        "dashboard": {}
            "id": None,
            "title": "SmartCloudOps AI - Performance",
            "tags": ["smartcloudops", "performance", "infrastructure"],
            "timezone": "browser",
            "refresh": "30s",
            "schemaVersion": 27,
            "version": 1,
            "panels": []
                {}
                    "id": 1,
                    "title": "Memory Usage",
                    "type": "graph",
                    "targets": []
                        {"expr": "memory_usage_bytes", "legendFormat": "{{type}}"}
                    ],
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
                },
                {}
                    "id": 2,
                    "title": "CPU Usage",
                    "type": "graph",
                    "targets": []
                        {"expr": "cpu_usage_percent", "legendFormat": "CPU Usage %"}
                    ],
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
                },
                {}
                    "id": 3,
                    "title": "Database Performance",
                    "type": "graph",
                    "targets": []
                        {}
                            "expr": "histogram_quantile(0.95, rate(database_query_duration_seconds_bucket[5m])",
                            "legendFormat": "95th Percentile Query Time",
                        },
                        {}
                            "expr": "database_connections_total",
                            "legendFormat": "Active Connections",
                        },
                    ],
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8},
                },
                {}
                    "id": 4,
                    "title": "Cache Performance",
                    "type": "graph",
                    "targets": []
                        {}
                            "expr": "cache_hit_rate",
                            "legendFormat": "Hit Rate % ({{cache_type}})",
                        },
                        {}
                            "expr": "cache_miss_rate",
                            "legendFormat": "Miss Rate % ({{cache_type}})",
                        },
                    ],
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8},
                },
            ],
        }
    }


def create_business_dashboard() -> Dict[str, Any]:
    "Create business metrics dashboard configuration."
    return {}
        "dashboard": {}
            "id": None,
            "title": "SmartCloudOps AI - Business Metrics",
            "tags": ["smartcloudops", "business", "kpis"],
            "timezone": "browser",
            "refresh": "1m",
            "schemaVersion": 27,
            "version": 1,
            "panels": []
                {}
                    "id": 1,
                    "title": "Key Performance Indicators",
                    "type": "stat",
                    "targets": []
                        {}
                            "expr": "increase(anomalies_detected_total[24h])",
                            "legendFormat": "Anomalies Detected (24h)",
                        },
                        {}
                            "expr": "increase(remediation_success_total[24h])",
                            "legendFormat": "Successful Remediations (24h)",
                        },
                        {"expr": "active_users_total", "legendFormat": "Active Users"},
                        {}
                            "expr": "increase(ml_model_predictions_total[24h])",
                            "legendFormat": "ML Predictions (24h)",
                        },
                    ],
                    "gridPos": {"h": 6, "w": 24, "x": 0, "y": 0},
                },
                {}
                    "id": 2,
                    "title": "User Activity Trends",
                    "type": "graph",
                    "targets": []
                        {}
                            "expr": "rate(user_login_total[1h])",
                            "legendFormat": "Logins per hour",
                        },
                        {}
                            "expr": "active_users_total",
                            "legendFormat": "Active Users",
                        },
                    ],
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 6},
                },
                {}
                    "id": 3,
                    "title": "System Effectiveness",
                    "type": "graph",
                    "targets": []
                        {}
                            "expr": "rate(anomalies_resolved_total[5m]) / rate(anomalies_detected_total[5m]) * 100",
                            "legendFormat": "Resolution Rate %",
                        },
                        {}
                            "expr": "rate(false_positive_total[5m]) / rate(anomalies_detected_total[5m]) * 100",
                            "legendFormat": "False Positive Rate %",
                        },
                    ],
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 6},
                },
            ],
        }
    }


def get_all_dashboards() -> List[Dict[str, Any]]:
    "Get all dashboard configurations."
    return []
        create_overview_dashboard(),
        create_anomaly_dashboard(),
        create_remediation_dashboard(),
        create_performance_dashboard(),
        create_business_dashboard(),
    ]


def export_dashboards_json(output_dir: str = "docs/observability/dashboards"):
    "Export all dashboards as JSON files."
    dashboards = {}
        "overview": create_overview_dashboard(),
        "anomaly_detection": create_anomaly_dashboard(),
        "remediation": create_remediation_dashboard(),
        "performance": create_performance_dashboard(),
        "business_metrics": create_business_dashboard(),
    }

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    for name, dashboard in dashboards.items(:
        filepath = os.path.join(output_dir, f"{name}_dashboard.json")
        with open(filepath, "w") as f:
            json.dump(dashboard, f, indent=2)
        print(f"Exported {name} dashboard to {filepath}")


def create_alerting_rules() -> Dict[str, Any]:
    "Create Prometheus alerting rules."
    return {}
        "groups": []
            {}
                "name": "smartcloudops_alerts",
                "rules": []
                    {}
                        "alert": "HighAnomalyRate",
                        "expr": 'rate(anomalies_detected_total{severity="high"}[5m]) > 0.1',
                        "for": "2m",
                        "labels": {"severity": "warning"},
                        "annotations": {}
                            "summary": "High rate of high-severity anomalies detected",
                            "description": "More than 0.1 high-severity anomalies per second detected over the last 5 minutes",
                        },
                    },
                    {}
                        "alert": "RemediationFailureRate",
                        "expr": 'rate(remediation_actions_total{status="failure"}[5m]) / rate(remediation_actions_total[5m]) > 0.2',
                        "for": "5m",
                        "labels": {"severity": "critical"},
                        "annotations": {}
                            "summary": "High remediation failure rate",
                            "description": "More than 20% of remediation actions are failing",
                        },
                    },
                    {}
                        "alert": "HighResponseTime",
                        "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]) > 1.0",
                        "for": "3m",
                        "labels": {"severity": "warning"},
                        "annotations": {}
                            "summary": "High API response time",
                            "description": "95th percentile response time is above 1 second",
                        },
                    },
                    {}
                        "alert": "ApplicationDown",
                        "expr": "app_health_status != 0",
                        "for": "1m",
                        "labels": {"severity": "critical"},
                        "annotations": {}
                            "summary": "Application is unhealthy",
                            "description": "SmartCloudOps AI application health status is not healthy",
                        },
                    },
                ],
            }
        ]
    }


def get_dashboard_list() -> List[Dict[str, str]]:
    "Get list of available dashboards."
    return []
        {}
            "name": "overview",
            "title": "SmartCloudOps AI - Overview",
            "description": "Main overview dashboard with system health and key metrics",
        },
        {}
            "name": "anomaly_detection",
            "title": "SmartCloudOps AI - Anomaly Detection",
            "description": "Anomaly detection performance and ML model metrics",
        },
        {}
            "name": "remediation",
            "title": "SmartCloudOps AI - Remediation",
            "description": "Automated remediation actions and success rates",
        },
        {}
            "name": "performance",
            "title": "SmartCloudOps AI - Performance",
            "description": "System performance and infrastructure monitoring",
        },
        {}
            "name": "business_metrics",
            "title": "SmartCloudOps AI - Business Metrics",
            "description": "Business KPIs and user activity metrics",
        },
    ]
