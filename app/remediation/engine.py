import os
import yaml
import threading
import logging
from typing import Dict, Any

from .actions import AWSActions
from .safety import SafetyController
from .notifications import Notifier

logger = logging.getLogger(__name__)


class RemediationEngine:
    """Evaluates rules and executes remediation actions safely."""

    def __init__(self, rules_path: str = "configs/remediation-rules.yaml"):
        self.rules_path = rules_path
        self.rules = self._load_rules()
        self.safety = SafetyController()
        self.notifier = Notifier()
        self.aws = AWSActions()

        self.require_approval: bool = (
            os.getenv("REQUIRE_APPROVAL", "false").lower() == "true"
        )
        self.tag_key: str = os.getenv("REMEDIATION_TAG_KEY", "Name")
        self.tag_value: str = os.getenv(
            "REMEDIATION_TAG_VALUE", "smartcloudops-ai-application"
        )
        self.service_name: str = os.getenv("SSM_SERVICE_NAME", "smartcloudops-app")
        self.approval_param: str = os.getenv(
            "APPROVAL_SSM_PARAM", "/smartcloudops/dev/approvals/auto"
        )
        self.region: str = os.getenv(
            "AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "us-west-2")
        )

    def _load_rules(self) -> Dict[str, Any]:
        try:
            with open(self.rules_path, "r") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            logger.warning(f"Rules file not found at {self.rules_path}; using defaults")
            return {"anomaly": {"severity_threshold": 0.7, "action": "restart_service"}}

    def handle_anomaly_async(self, anomaly_result: Dict[str, Any]) -> None:
        threading.Thread(
            target=self._handle_anomaly, args=(anomaly_result,), daemon=True
        ).start()

    def _handle_anomaly(self, anomaly_result: Dict[str, Any]) -> None:
        try:
            if anomaly_result.get("status") != "success":
                return
            if not anomaly_result.get("is_anomaly"):
                return

            severity = float(anomaly_result.get("severity_score", 0.0))
            threshold = float(
                self.rules.get("anomaly", {}).get("severity_threshold", 0.7)
            )
            if severity < threshold:
                return

            action = self.rules.get("anomaly", {}).get("action", "restart_service")
            if action == "restart_service":
                self._execute_restart_service(
                    reason=f"Anomaly severity {severity} >= {threshold}"
                )
        except Exception as exc:
            logger.error(f"Error in remediation handling: {exc}")

    def _execute_restart_service(self, reason: str) -> None:
        resource_id = f"tag:{self.tag_key}={self.tag_value}"
        allowed, why = self.safety.allow("restart_service", resource_id)
        if not allowed:
            logger.info(f"Safety block: {why}")
            self.notifier.send_slack_message(
                title="Remediation Blocked (Safety)",
                message=why,
                fields={
                    "action": "restart_service",
                    "resource": resource_id,
                    "reason": reason,
                },
            )
            return

        if self.require_approval:
            # Check approval flag from SSM parameter (boolean string 'true')
            try:
                import boto3

                ssm = boto3.client("ssm", region_name=self.region)
                resp = ssm.get_parameter(Name=self.approval_param, WithDecryption=False)
                value = (
                    resp.get("Parameter", {}).get("Value", "false").lower() == "true"
                )
            except Exception:
                value = False

            if not value:
                self.notifier.send_slack_message(
                    title="Approval Required: Restart Service",
                    message=reason,
                    fields={
                        "resource": resource_id,
                        "service": self.service_name,
                        "approval_param": self.approval_param,
                    },
                )
                logger.info("Approval required; awaiting approval flag in SSM")
                return

        result = self.aws.restart_service_via_ssm(
            tag_key=self.tag_key,
            tag_value=self.tag_value,
            service_name=self.service_name,
        )
        if result.get("status") == "success":
            self.safety.record("restart_service", resource_id)
            self.notifier.send_slack_message(
                title="Remediation Executed: Restart Service",
                message=reason,
                fields={
                    "instances": ",".join(result.get("instances", [])),
                    "service": self.service_name,
                },
            )
        else:
            self.notifier.send_slack_message(
                title="Remediation Failed: Restart Service",
                message=result.get("message", "unknown error"),
                fields={"resource": resource_id, "service": self.service_name},
            )
