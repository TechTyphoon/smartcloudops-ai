# Syntax Error Report - SmartCloudOps.AI

Generated: 2025-08-28T18:17:54.283954

## Summary

⚠️ **Found 191 file(s) with syntax errors**

### Errors by File Type:
- **Python**: 78 file(s)
- **Javascript**: 1 file(s)
- **Typescript**: 112 file(s)

## Detailed Error List

### Python Files

#### `scripts/monitoring/real_system_monitor.py`
```
Line 163: unterminated f-string literal (detected at line 163)
    f"  Memory Usage: {real_metrics['memory']['usage_percent']}% (
            ^
```

#### `scripts/monitoring/uptime_monitor.py`
```
Line 21: invalid syntax
    """Check if a service is up""f"
           ^
```

#### `scripts/monitoring/continuous_health_monitor.py`
```
Line 216: unterminated f-string literal (detected at line 216)
    f"✅ {endpoint} - {result['status_code']} (
                        ^
```

#### `scripts/security/validate_secrets.py`
```
Line 12: unterminated string literal (detected at line 12)
    r'password\s*=\s*["\'][^f"\f']{3,}["\']',
                                           ^
```

#### `scripts/testing/production_validation.py`
```
Line 65: unterminated string literal (detected at line 65)
    "   smartcloudops-main      Up 45 minutes (
                        ^
```

#### `scripts/testing/health_check.py`
```
Line 30: unterminated f-string literal (detected at line 30)
    "message": f"Flask endpoints failed: health={health_response.status_code},
                                   ^
```

#### `ml_models/model_versioning.py`
```
Line 327: invalid syntax
    """Update performance metrics in model version"""
               ^
```

#### `tests/test_integration.py`
```
Line 41: invalid syntax
    """Mock anomaly detector for testing.""f"
               ^
```

#### `tests/test_ml_anomaly_detection.py`
```
Line 11: unexpected indent
    AnomalyInferenceEngine,
       ^
```

#### `tests/test_remediation.py`
```
Line 26: invalid syntax
    """Test remediation engine initialization."""
               ^
```

#### `tests/test_gpt_integration.py`
```
Line 19: invalid syntax
    """Test GPT handler initialization with API key."""
               ^
```

#### `tests/test_ai_handler.py`
```
Line 21: invalid syntax
    """Test handler initialization with OpenAI API key."""
               ^
```

#### `tests/test_chatops.py`
```
Line 10: unexpected indent
    SystemContextGatherer,
       ^
```

#### `tests/test_ml_endpoints.py`
```
Line 95: invalid syntax
    """Test batch anomaly detection with no data."""
               ^
```

#### `tests/unit/test_ml_models.py`
```
Line 49: invalid syntax
    """Test anomaly detector initialization."""
               ^
```

#### `tests/unit/test_remediation_engine.py`
```
Line 22: invalid syntax
    """Create remediation engine instance for testing."""
               ^
```

#### `tests/integration/test_api_endpoints.py`
```
Line 37: invalid syntax
    """Create test client."""
               ^
```

#### `tests/backend/test_chatops.py`
```
Line 34: invalid syntax
    """Test /chatops/analyze endpoint with missing query."""
           ^
```

#### `app/auth_routes.py`
```
Line 4: unexpected indent
    """
       ^
```

#### `app/ml_module.py`
```
Line 3: unexpected indent
    """
       ^
```

#### `app/chatops_module.py`
```
Line 3: unexpected indent
    """
       ^
```

#### `app/auth.py`
```
Line 104: unexpected indent
    user_id=user_id,
                       ^
```

#### `app/monitoring/metrics.py`
```
Line 2: unexpected indent
    """
       ^
```

#### `app/api/performance.py`
```
Line 166: closing parenthesis '}' does not match opening parenthesis '(' on line 162
    })
            ^
```

#### `app/api/anomalies_refactored.py`
```
Line 2: unexpected indent
    """
       ^
```

#### `app/api/ai.py`
```
Line 177: cannot assign to subscript here. Maybe you meant '==' instead of '='?
    analysis_result["anomaly_detected"] = False
            ^
```

#### `app/api/mlops.py`
```
Line 2: unexpected indent
    """
       ^
```

#### `app/mlops/dataset_manager.py`
```
Line 3: unterminated string literal (detected at line 3)
    """"
       ^
```

#### `app/mlops/reinforcement_learning.py`
```
Line 6: unterminated string literal (detected at line 6)
    "
    ^
```

#### `app/mlops/data_pipeline.py`
```
Line 2: unexpected indent
    """
       ^
```

#### `app/mlops/experiment_tracker.py`
```
Line 94: unmatched ')'
    )
            ^
```

#### `app/mlops/model_registry.py`
```
Line 96: unmatched ')'
    )
            ^
```

#### `app/mlops/training_pipeline.py`
```
Line 3: unterminated string literal (detected at line 3)
    """"
       ^
```

#### `app/mlops/model_monitor.py`
```
Line 337: closing parenthesis '}' does not match opening parenthesis '(' on line 328
    })
                        ^
```

#### `app/mlops/reproducibility.py`
```
Line 3: unterminated string literal (detected at line 3)
    """"
       ^
```

#### `app/mlops/knowledge_base.py`
```
Line 2: unexpected indent
    """
       ^
```

#### `app/mlops/model_registry_minimal.py`
```
Line 96: unmatched ')'
    )
            ^
```

#### `app/mlops/experiment_tracker_minimal.py`
```
Line 94: unmatched ')'
    )
            ^
```

#### `app/mlops/autonomous_ops.py`
```
Line 2: unexpected indent
    """
       ^
```

#### `app/mlops/data_pipeline_enhanced.py`
```
Line 2: unexpected indent
    """
       ^
```

#### `app/analytics/real_time_dashboard.py`
```
Line 5: unexpected indent
    """
       ^
```

#### `app/remediation/engine.py`
```
Line 2: unterminated string literal (detected at line 2)
    "
    ^
```

#### `app/remediation/safety.py`
```
Line 5: unterminated string literal (detected at line 5)
    "
    ^
```

#### `app/remediation/__init__.py`
```
Line 1: unterminated triple-quoted string literal (detected at line 1)
    """Auto-remediation package for Smart CloudOps AI (Phase 4)."
    ^
```

#### `app/remediation/notifications.py`
```
Line 4: unterminated string literal (detected at line 4)
    "
    ^
```

#### `app/remediation/actions.py`
```
Line 4: unterminated string literal (detected at line 4)
    "
    ^
```

#### `app/performance/anomaly_optimization.py`
```
Line 98: unmatched ')'
    )
                ^
```

#### `app/performance/database_optimization.py`
```
Line 113: closing parenthesis '}' does not match opening parenthesis '(' on line 109
    })
                    ^
```

#### `app/performance/log_optimization.py`
```
Line 59: expected an indented block after function definition on line 58
    """Initialize current log file"""
        ^
```

#### `app/performance/redis_cache.py`
```
Line 62: unexpected indent
    **asdict(self),
               ^
```

#### `app/performance/caching.py`
```
Line 67: unexpected indent
    "hits": self.hits,
               ^
```

#### `app/performance/__init__.py`
```
Line 12: unexpected indent
    "cache_manager",
           ^
```

#### `app/performance/api_optimization.py`
```
Line 75: unmatched '}'
    }
                        ^
```

#### `app/chatops/gpt_handler.py`
```
Line 175: expected an indented block after function definition on line 172
    """Process ChatOps query with GPT integration and enhanced security.""":
        ^
```

#### `app/chatops/ai_handler.py`
```
Line 4: unexpected indent
    """
       ^
```

#### `app/chatops/utils.py`
```
Line 7: unexpected indent
    """
       ^
```

#### `app/security/secrets_manager.py`
```
Line 3: unterminated string literal (detected at line 3)
    "
    ^
```

#### `app/security/config.py`
```
Line 281: closing parenthesis '}' does not match opening parenthesis '(' on line 274
    }
            ^
```

#### `app/security/input_validation.py`
```
Line 4: unterminated string literal (detected at line 4)
    "
    ^
```

#### `app/security/error_handling.py`
```
Line 2: unexpected indent
    """
       ^
```

#### `app/security/rate_limiting.py`
```
Line 2: unexpected indent
    """
       ^
```

#### `app/security/caching.py`
```
Line 4: unterminated string literal (detected at line 4)
    "
    ^
```

#### `app/services/ml_service.py`
```
Line 2: unexpected indent
    """
       ^
```

#### `app/services/mlops_service.py`
```
Line 2: unexpected indent
    """
       ^
```

#### `app/services/feedback_service.py`
```
Line 2: unexpected indent
    """
       ^
```

#### `app/services/security_validation.py`
```
Line 27: unmatched ']'
    ]
            ^
```

#### `app/services/anomaly_service.py`
```
Line 2: unexpected indent
    """
       ^
```

#### `app/services/ai_service.py`
```
Line 2: unexpected indent
    """
       ^
```

#### `app/services/remediation_service.py`
```
Line 2: unexpected indent
    """
       ^
```

#### `app/observability/opentelemetry_config.py`
```
Line 46: unmatched ')'
    console_export: bool = False) -> None:
                                        ^
```

#### `app/observability/slos.py`
```
Line 73: unmatched ')'
    )
            ^
```

#### `app/observability/metrics.py`
```
Line 72: unexpected indent
    "anomalies_detected_total",
       ^
```

#### `app/observability/middleware.py`
```
Line 3: unterminated string literal (detected at line 3)
    """"
       ^
```

#### `app/observability/logging_config.py`
```
Line 27: unmatched ')'
    message_dict: Dict[str, Any]) -> None:
                                        ^
```

#### `app/observability/tracing.py`
```
Line 62: unmatched ')'
    enable_auto_instrumentation: bool = True) -> bool:
                                                ^
```

#### `app/observability/enhanced_logging.py`
```
Line 39: unmatched ')'
    message_dict: Dict[str, Any]) -> None:
                                        ^
```

#### `app/observability/dashboards.py`
```
Line 2: unexpected indent
    """
       ^
```

#### `app/observability/__init__.py`
```
Line 11: unexpected indent
    "setup_logging",
       ^
```

### Javascript Files

#### `scripts/performance/k6_load_test.js`
```
Unexpected token ':'
```

### Typescript Files

#### `smartcloudops-ai/vitest.config.ts`
```
Unexpected token ':'
```

#### `smartcloudops-ai/components/anomaly-details-modal.tsx`
```
Unexpected identifier 'AnomalyDetailsModalProps'
```

#### `smartcloudops-ai/components/audit-log.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/components/real-time-status.tsx`
```
Unexpected identifier 'RealTimeStatusProps'
```

#### `smartcloudops-ai/components/sidebar.tsx`
```
Unexpected identifier 'SidebarProps'
```

#### `smartcloudops-ai/components/chatops-interface.tsx`
```
Unexpected identifier 'Message'
```

#### `smartcloudops-ai/components/action-log.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/components/header.tsx`
```
Unexpected token '}'
```

#### `smartcloudops-ai/components/anomaly-card.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/components/welcome-hero.tsx`
```
Unexpected token '<'
```

#### `smartcloudops-ai/components/service-dependency-graph.tsx`
```
Unexpected token ']'
```

#### `smartcloudops-ai/components/cost-optimization-card.tsx`
```
Unexpected identifier 'undefined'
```

#### `smartcloudops-ai/components/sla-indicator.tsx`
```
Unexpected identifier 'undefined'
```

#### `smartcloudops-ai/components/theme-provider.tsx`
```
Unexpected identifier 'as'
```

#### `smartcloudops-ai/components/monitoring-dashboard.tsx`
```
Unexpected identifier 'SystemMetric'
```

#### `smartcloudops-ai/components/dashboard-layout.tsx`
```
Unexpected identifier 'DashboardLayoutProps'
```

#### `smartcloudops-ai/components/remediation-action-card.tsx`
```
Unexpected token '}'
```

#### `smartcloudops-ai/components/monitoring/monitoring-dashboard.tsx`
```
Unexpected token '}'
```

#### `smartcloudops-ai/components/auth/login-form.tsx`
```
missing ) after argument list
```

#### `smartcloudops-ai/components/auth/protected-route.tsx`
```
Unexpected identifier 'ProtectedRouteProps'
```

#### `smartcloudops-ai/components/mlops/data-pipeline-panel.tsx`
```
Unexpected identifier 'from'
```

#### `smartcloudops-ai/components/mlops/mlops-overview.tsx`
```
Unexpected identifier 'from'
```

#### `smartcloudops-ai/components/mlops/models-panel.tsx`
```
Unexpected identifier 'from'
```

#### `smartcloudops-ai/components/mlops/mlops-status-bar.tsx`
```
Unexpected identifier 'from'
```

#### `smartcloudops-ai/components/mlops/experiments-panel.tsx`
```
Unexpected identifier 'from'
```

#### `smartcloudops-ai/components/ui/alert-dialog.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/components/ui/chart.tsx`
```
Unexpected identifier 'as'
```

#### `smartcloudops-ai/components/ui/separator.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/components/ui/menubar.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/components/ui/tooltip.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/components/ui/loading-skeleton.tsx`
```
Unexpected token '<'
```

#### `smartcloudops-ai/components/ui/navigation-menu.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/components/ui/textarea.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/components/ui/card.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/components/ui/enhanced-themes.tsx`
```
Unexpected identifier 'as'
```

#### `smartcloudops-ai/components/ui/carousel.tsx`
```
Unexpected identifier 'UseEmblaCarouselType'
```

#### `smartcloudops-ai/components/ui/label.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/components/ui/toaster.tsx`
```
Unexpected token '}'
```

#### `smartcloudops-ai/components/ui/scroll-area.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/components/ui/sonner.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/components/ui/input-otp.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/components/ui/pagination.tsx`
```
Unexpected token '}'
```

#### `smartcloudops-ai/components/ui/aspect-ratio.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/components/ui/sidebar.tsx`
```
Unexpected token '}'
```

#### `smartcloudops-ai/components/ui/dropdown-menu.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/components/ui/use-toast.ts`
```
Unexpected token '}'
```

#### `smartcloudops-ai/components/ui/slider.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/components/ui/dialog.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/components/ui/popover.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/components/ui/toggle-group.tsx`
```
Unexpected token '>'
```

#### `smartcloudops-ai/components/ui/alert.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/components/ui/select.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/components/ui/input.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/components/ui/use-mobile.tsx`
```
Unexpected token '}'
```

#### `smartcloudops-ai/components/ui/error-boundary.tsx`
```
Unexpected identifier 'ErrorBoundaryState'
```

#### `smartcloudops-ai/components/ui/collapsible.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/components/ui/form.tsx`
```
Unexpected identifier 'ControllerProps'
```

#### `smartcloudops-ai/components/ui/drawer.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/components/ui/sheet.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/components/ui/button.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/components/ui/calendar.tsx`
```
Unexpected token '}'
```

#### `smartcloudops-ai/components/ui/command.tsx`
```
Unexpected token '}'
```

#### `smartcloudops-ai/components/ui/accordion.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/components/ui/checkbox.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/components/ui/breadcrumb.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/components/ui/responsive-container.tsx`
```
Unexpected identifier 'ResponsiveContainerProps'
```

#### `smartcloudops-ai/components/ui/hover-card.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/components/ui/radio-group.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/components/ui/context-menu.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/components/ui/resizable.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/components/ui/toast.tsx`
```
Unexpected token ','
```

#### `smartcloudops-ai/components/ui/skeleton.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/components/ui/avatar.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/components/ui/toggle.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/components/ui/switch.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/components/ui/badge.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/components/ui/progress.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/components/ui/table.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/components/ui/tabs.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/__tests__/setup.ts`
```
Unexpected token ':'
```

#### `smartcloudops-ai/__tests__/components/mlops/mlops-overview.test.tsx`
```
Unexpected token '<'
```

#### `smartcloudops-ai/__tests__/utils/test-utils.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/hooks/use-websocket.tsx`
```
Unexpected identifier 'WebSocketConfig'
```

#### `smartcloudops-ai/hooks/use-auth.tsx`
```
Unexpected identifier 'User'
```

#### `smartcloudops-ai/hooks/use-toast.ts`
```
Unexpected token '}'
```

#### `smartcloudops-ai/hooks/use-real-time-metrics.tsx`
```
Unexpected identifier 'MetricData'
```

#### `smartcloudops-ai/hooks/use-mlops-real-time.tsx`
```
Unexpected identifier 'UseMLOpsRealTimeOptions'
```

#### `smartcloudops-ai/hooks/use-mobile.ts`
```
Unexpected token '}'
```

#### `smartcloudops-ai/app/page.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/app/layout.tsx`
```
Unexpected token ':'
```

#### `smartcloudops-ai/app/monitoring/page.tsx`
```
Unexpected token '<'
```

#### `smartcloudops-ai/app/mlops/page.tsx`
```
Unexpected identifier 'from'
```

#### `smartcloudops-ai/app/remediation/page.tsx`
```
Unexpected token ']'
```

#### `smartcloudops-ai/app/remediation/loading.tsx`
```
Unexpected token '}'
```

#### `smartcloudops-ai/app/insights/page.tsx`
```
Missing initializer in const declaration
```

#### `smartcloudops-ai/app/insights/loading.tsx`
```
Unexpected token '}'
```

#### `smartcloudops-ai/app/chatops/page.tsx`
```
Unexpected token '<'
```

#### `smartcloudops-ai/app/settings/page.tsx`
```
Unexpected token '<'
```

#### `smartcloudops-ai/app/anomalies/page.tsx`
```
Unexpected token ']'
```

#### `smartcloudops-ai/app/anomalies/loading.tsx`
```
Unexpected token '}'
```

#### `smartcloudops-ai/app/anomalies/[id]/page.tsx`
```
Unexpected identifier 'from'
```

#### `smartcloudops-ai/app/login/page.tsx`
```
Unexpected token '<'
```

#### `tests/e2e/global-teardown.ts`
```
Unexpected token ':'
```

#### `tests/e2e/global-setup.ts`
```
Unexpected token ':'
```

#### `tests/e2e/playwright.config.ts`
```
Unexpected token ':'
```

#### `tests/e2e/tests/performance.spec.ts`
```
Unexpected token ':'
```

#### `tests/e2e/tests/dashboard.spec.ts`
```
Unexpected token ':'
```

#### `tests/e2e/tests/accessibility.spec.ts`
```
Unexpected token ':'
```

#### `tests/e2e/pages/DashboardPage.ts`
```
Unexpected identifier 'page'
```

#### `tests/e2e/pages/LoginPage.ts`
```
Unexpected identifier 'page'
```

#### `tests/e2e/utils/accessibility-utils.ts`
```
missing ) after argument list
```

#### `tests/e2e/utils/test-helpers.ts`
```
missing ) after argument list
```