import os
import json
import logging
from typing import Dict, Any, Optional

import requests

logger = logging.getLogger(__name__)


class Notifier:
    """Notifier for sending remediation events to Slack via webhook."""

    def __init__(self, slack_webhook_url: Optional[str] = None):
        self.slack_webhook_url = slack_webhook_url or os.getenv("SLACK_WEBHOOK_URL", "")

    def send_slack_message(self, title: str, message: str, fields: Optional[Dict[str, Any]] = None) -> bool:
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
            response = requests.post(self.slack_webhook_url, data=json.dumps(payload), headers={"Content-Type": "application/json"}, timeout=10)
            if response.status_code >= 200 and response.status_code < 300:
                return True
            logger.warning(f"Slack webhook failed with status {response.status_code}: {response.text}")
            return False
        except Exception as exc:
            logger.error(f"Failed to send Slack notification: {exc}")
            return False
