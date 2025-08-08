import os
import json
import logging
from typing import Dict, Any, Optional

import requests
import boto3

logger = logging.getLogger(__name__)


class Notifier:
    """Notifier for sending remediation events to Slack via webhook."""

    def __init__(self, slack_webhook_url: Optional[str] = None):
        # Load from env first; if not present, fall back to AWS SSM Parameter Store
        self.slack_webhook_url = slack_webhook_url or os.getenv("SLACK_WEBHOOK_URL", "")
        if not self.slack_webhook_url:
            self._load_webhook_from_ssm()

    def _load_webhook_from_ssm(self) -> None:
        """Load Slack webhook from AWS SSM Parameter Store if configured."""
        try:
            param_name = os.getenv(
                "SSM_PARAM_SLACK_WEBHOOK", "/smartcloudops/dev/slack/webhook"
            )
            region = os.getenv(
                "AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "us-west-2")
            )
            ssm = boto3.client("ssm", region_name=region)
            resp = ssm.get_parameter(Name=param_name, WithDecryption=True)
            self.slack_webhook_url = resp.get("Parameter", {}).get("Value", "")
            if self.slack_webhook_url:
                logger.info(f"Loaded Slack webhook from SSM parameter: {param_name}")
            else:
                logger.warning("Slack webhook not found in SSM parameter response")
        except Exception as exc:
            logger.warning(f"Could not load Slack webhook from SSM: {exc}")

    def send_slack_message(
        self, title: str, message: str, fields: Optional[Dict[str, Any]] = None
    ) -> bool:
        if not self.slack_webhook_url:
            logger.info("Slack webhook URL not configured; skipping notification")
            return False

        payload = {
            "text": f"*{title}*\n{message}",
        }

        if fields:
            formatted_fields = "\n".join([f"- {k}: `{v}`" for k, v in fields.items()])
            payload["text"] += f"\n{formatted_fields}"

        try:
            response = requests.post(
                self.slack_webhook_url,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            if response.status_code >= 200 and response.status_code < 300:
                return True
            logger.warning(
                f"Slack webhook failed with status {response.status_code}: {response.text}"
            )
            return False
        except Exception as exc:
            logger.error(f"Failed to send Slack notification: {exc}")
            return False
