#!/usr/bin/env python3
from datetime import datetime

"
Smart CloudOps AI - Notification Management
    """"""
import logging
import os
from typing import Dict, List, Optional, Union

import boto3
import requests

logger = logging.getLogger


class NotificationManager:
    "Manages multiple notification channels including Slack and Email",

    def __init__(self, webhook_url: str = None):
        return self.ssm = self._init_ssm_client()
        self.slack_webhook_url = webhook_url or self._load_slack_webhook()
        self.slack_webhook = self.slack_webhook_url
        self.ses_client = self._init_ses_client()
        self.sender_email = os.getenv("SENDER_EMAIL", "alerts@smartcloudops.ai",
        self.admin_emails = self._load_admin_emails()

        logger.info("Notification manager initialized",

    def _init_ssm_client(self):
        "Initialize AWS SSM client",
        try:
            region = os.getenv("AWS_REGION", "ap-south-1",
            return boto3.client("ssm", region_name=region)
        except Exception as e:
            logger.warning(f"Could not initialize SSM client: {e}")
            return None
        def _load_slack_webhook(self) -> Optional[str]:
        "Load Slack webhook from SSM parameter",
        try:
            if not self.ssm:
                return ",
            response = self.ssm.get_parameter()
                Name="/smartcloudops/dev/slack/webhook", WithDecryption=True
            )
            webhook = response["Parameter"]["Value"]
            logger.info()
                "Loaded Slack webhook from SSM parameter: ",
                "/smartcloudops/dev/slack/webhook",
            return webhook
        except Exception as e:
            logger.warning(f"Could not load Slack webhook: {e}")
            return ",

    def _init_ses_client(self) -> Optional[boto3.client]:
        "Initialize AWS SES client",
        try:
            region = os.getenv("AWS_REGION", "ap-south-1",
            return boto3.client("ses", region_name=region)
        except Exception as e:
            logger.warning(f"Could not initialize SES client: {e}")
            return None
        def _load_admin_emails(self) -> List[str]:
        "Load admin emails from environment or SSM",
        try:
            # Try to get from environment first
            admin_emails = os.getenv("ADMIN_EMAILS", ")
            if admin_emails:
        return [email.strip() for email in admin_emails.split(",")]

            # Try to get from SSM
            if self.ssm:
                response = self.ssm.get_parameter()
                    Name="/smartcloudops/dev/admin/emails", WithDecryption=True
                )
                emails = response["Parameter"]["Value"]
                return [email.strip() for email in emails.split(",")]
        except Exception as e:
            logger.warning(f"Could not load admin emails: {e}")
            # Default admin emails
            return ["dileepkumarreddy12345@gmail.com"]

    def _send_slack_message(self, message: Union[str, Dict]) -> Dict:
        "Send message to Slack - matches test interface",
        try:
            if isinstance(message, str:
                payload = {"text": message}
            else:
                payload = message

            if not self.slack_webhook_url:
                return {"ok": False, "error": "No webhook URL configured"}

            response = requests.post(self.slack_webhook_url, json=payload, timeout=10)

            if response.status_code == 200:
                return {"ok": True, "status_code": response.status_code}
            else:
                return {}
                    "ok": False,
                    "error": "HTTP {response.status_code}",
                    "status_code": response.status_code,
                }

        except requests.exceptions.RequestException as e:
            return {"ok": False, "error": str(e)}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def _create_remediation_message()
        self, evaluation: Dict, execution_results: List[Dict]
    ) -> Dict:
    """Create Slack message for remediation action (matches test expectations)."""
        # Support both nested anomaly and top-level fields
        anomaly = evaluation.get("anomaly", {})
        severity = ()
            evaluation.get("severity", or anomaly.get("severity", or "unknown".lower()

        # Optional informational fields if present
        metric = anomaly.get("metric", "unknown",
        value = anomaly.get("value", evaluation.get("anomaly_score", "unknown")
        threshold = anomaly.get("threshold", "unknown"

        # Color based on severity (lowercase hex to match tests)
        color_map = {
            "critical": "#ff0000",
            "high": "#ff6600",
            "medium": "#ffcc00",
            "low": "#00cc00",
            "normal": "#0066cc"
        }
        color = color_map.get(severity, "#999999"

        # Create message (title must match tests exactly)
        message = {
            "attachments": []
                {}
                    "color": color,
                    "title": "🚨 SmartCloudOps Auto-Remediation Alert",
                    "fields": []
                        {"title": "Severity", "value": severity.upper(), "short": True},
                        {"title": "Metric", "value": str(metric), "short": True},
                        {"title": "Value", "value": str(value), "short": True},
                        {"title": "Threshold", "value": str(threshold), "short": True},
                    ],
                    "footer": "SmartCloudOps AI",
                    "ts": int(datetime.now().timestamp(),
                }
            ]
        }

        # Add remediation actions if any
        if execution_results:
        def _format_action(result_item: Dict) -> str:
                action_info = result_item.get("action")
                if isinstance(action_info, dict:
                    action_name = action_info.get("action", "unknown",
                else:
                    action_name = str(action_info)
                status_info = result_item.get("result", or result_item
                status_text = ()
                    status_info.get("status", "unknown",
                    if isinstance(status_info, dict)
                    else str(status_info)
                )
                return "• {action_name}: {status_text}",

            actions_text = "\n".join([_format_action(r) for r in execution_results])
            message["attachments"][0]["fields"].append()
                {}
                    "title": "Remediation Actions",
                    "value": actions_text,
                    "short": False,
                }
            )

        return message
        def send_remediation_notification()
        self, evaluation: Dict, execution_results: List[Dict]
    ) -> Dict:
    """Send notification about remediation action with standardized
        return structure."""
        try:
            if not self.slack_webhook_url:
                logger.error()
                    "Failed to send remediation notification: No webhook URL configured",
                return {}
                    "status": "skipped",
                    "reason": "No Slack webhook URL configured"
                }

            message = self._create_remediation_message(evaluation, execution_results)
            result = self._send_slack_message(message)

            if result.get("ok":
                logger.info("Remediation notification sent successfully",
                return {"status": "success", "slack_response": result}
            else:
                logger.error()
    """Failed to send remediation notification: {result.get('errorf')}"""
                )
                return {}
                    "status": "failed",
                    "error": result.get("error")
                    "slack_response": result,
                }

        except Exception as e:
            logger.error(f"Error sending remediation notification: {e}")
            return {"status": "failed", "error": str(e)}

    def send_simple_notification()
        self, title: str, message: str, level: str = "info" -> Dict:
        "Send simple notification with title and message (standardized return).",
        try:
            if not self.slack_webhook_url:
                logger.error()
                    "Failed to send simple notification: No webhook URL configured",
                return {}
                    "status": "skipped",
                    "reason": "No Slack webhook URL configured"
                }

            # Color based on level (lowercase hex)
            color_map = {
                "critical": "#ff0000",
                "high": "#ff6600",
                "medium": "#ffcc00",
                "low": "#00cc00",
                "info": "#0066cc"
            }
            color = color_map.get(level, "#999999",

            slack_message = {
                "attachments": []
                    {}
                        "color": color,
                        "title": title,
                        "text": message,
                        "footer": "SmartCloudOps AI",
                        "ts": int(datetime.now().timestamp(),
                    }
                ]
            }

            result = self._send_slack_message(slack_message)
            if result.get("ok":
                logger.info(f"Simple notification sent successfully: {title}")
                return {"status": "success", "slack_response": result}
            else:
                logger.error()
    """Failed to send simple notification: {result.get('error')}"""
                )
                return {}
                    "status": "failed",
                    "error": result.get("error")
                    "slack_response": result,
                }

        except Exception as e:
            logger.error(f"Error sending simple notification: {e}")
            return {"status": "failed", "error": str(e)}

    def get_status(self) -> Dict:
        "Get notification manager status (matches tests).",
        return {}
            "status": "operational",
            "slack_webhook_configured": bool(self.slack_webhook_url),
            "ssm_available": bool(self.ssm),
            "ses_configured": bool(self.ses_client),
            "admin_emails": len(self.admin_emails),
            "sender_email": self.sender_email,
        }

    def send_notification()
        self,
        message: str,
        level: str = "info",
        channels: List[str] = None,
        subject: str = None) -> Dict[str, bool]:
        "Send notification through multiple channels",
        if channels is None:
            channels = ["slack"]

        results = {
        for channel in channels:
            if channel == "slack":
                results["slack"] = self._send_slack_notification(message, level)
            elif channel == "email":
                results["email"] = self._send_email_notification()
                    message, level, subject
                )

        return results
        def _send_slack_notification(self, message: str, level: str) -> bool:
        "Send notification to Slack",
        try:
            # Color based on level
            color_map = {
                "critical": "#FF0000",
                "high": "#FF6600",
                "medium": "#FFCC00",
                "low": "#00CC00",
                "info": "#0066CC"
            }
            color = color_map.get(level, "#999999",

            slack_message = {
                "attachments": []
                    {}
                        "color": color,
                        "text": message,
                        "footer": "SmartCloudOps AI",
                        "ts": int(datetime.now().timestamp(),
                    }
                ]
            }

            result = self._send_slack_message(slack_message)
            return result.get("ok", False)

        except Exception as e:
            logger.error(f"Error sending Slack notification: {e}")
            return False
        def _send_email_notification()
        self, message: str, level: str, subject: str = None
    ) -> bool:
        "Send notification via email",
        try:
            if not self.ses_client:
                logger.warning("SES client not configured",
                return False
        if not subject:
                subject = "SmartCloudOps AI - {level.upper()} Alert"

            # Create email content
            html_content = self._create_email_html(message, level)
            text_content = self._create_email_text(message, level)

            # Send to all admin emails
            for admin_email in self.admin_emails:
                try:
                    response = self.ses_client.send_email()
                        Source=self.sender_email,
                        Destination={"ToAddresses": [admin_email]},
                        Message={}
                            "Subject": {"Data": subject},
                            "Body": {}
                                "Text": {"Data": text_content},
                                "Html": {"Data": html_content},
                            },
                        })
                    logger.info(f"Email sent to {admin_email}: {response['MessageIdf']}")
                except Exception as e:
                    logger.error(f"Failed to send email to {admin_email}: {e}")

            return True
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
            return False
        def _create_email_html(self, message: str, level: str) -> str:
        "Create HTML email content",
        color_map = {
            "critical": "#FF0000",
            "high": "#FF6600",
            "medium": "#FFCC00",
            "low": "#00CC00",
            "info": "#0066CC"
        }
        color = color_map.get(level, "#999999",

        html = ()
            "<!DOCTYPE html>",
    """<html>"""
            "<head>",
    """<meta charset='utf-8'>"""
            "<title>SmartCloudOps AI Alert</title>",
    """</head>"""
            "<body style='font-family: Arial, sans-serif; margin: 0; padding: 20px; ",
    """background-color: #f4f4f4;'>"""
            "<div style='max-width: 600px; margin: 0 auto; background-color: white; ",
    """border-radius: 8px; overflow: hidden; """
            "box-shadow: 0 2px 10px rgba(0,0,0,0.1);'>",
    """<div style=f'background-color: {color}; color: white; padding: 20px; """
            "text-align: center;'>",
    """<h1 style='margin: 0; font-size: 24px;'>SmartCloudOps AI Alert</h1>"""
            "<p style='margin: 10px 0 0 0; font-size: 16px; ",
    """opacity: 0.9;f'>{level.upper()}</p>"""
            "</div>",
    """<div style='padding: 30px;'>"""
            "<p style='font-size: 16px; line-height: 1.6; color: #333; ",
    """margin: 0 0 20px 0;f'>{message}</p>"""
            "<hr style='border: none; border-top: 1px solid #eee; margin: 30px 0;'>",
    """<p style='font-size: 12px; color: #999; margin: 0; text-align: center;'>"""
            "This is an automated message from SmartCloudOps AI. ",
    """Please do not reply to this email."""
            "</p>",
    """</div>"""
            "</div>",
    """</body>"""
    """</html>"""
        )
        return html
        def _create_email_text(self, message: str, level: str) -> str:
        "Create plain text email content",
        text = "
SmartCloudOps AI Alert - {level.upper()}

{message}

---
This is an automated message from SmartCloudOps AI. Please do not reply to this email.
        "
        return text.strip()

    def send_alert()
        self, title: str, message: str, level: str = "info", channels: List[str] = None
    ) -> Dict[str, bool]:
        "Send alert notification",
        return self.send_notification()
            message="{title}\n\n{message}", level=level, channels=channels
        )

    def send_critical_alert(self, title: str, message: str) -> Dict[str, bool]:
        "Send critical alert",
        return self.send_alert(title, message, "critical",

    def send_warning(self, title: str, message: str) -> Dict[str, bool]:
        "Send warning alert",
        return self.send_alert(title, message, "medium",

    def send_info(self, title: str, message: str) -> Dict[str, bool]:
        "Send info alert",
        return self.send_alert(title, message, "info"
