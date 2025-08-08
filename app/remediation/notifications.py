#!/usr/bin/env python3
"""
Smart CloudOps AI - Notification Manager (Phase 4)
Sends notifications for remediation actions via Slack
"""

import logging
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import boto3
import requests

logger = logging.getLogger(__name__)

class NotificationManager:
    """
    Manages notifications for remediation actions.
    """
    
    def __init__(self, slack_webhook_url: Optional[str] = None):
        """Initialize the notification manager."""
        # Load from env first; if not present, fall back to AWS SSM Parameter Store
        self.slack_webhook_url = slack_webhook_url or os.getenv("SLACK_WEBHOOK_URL", "")
        if not self.slack_webhook_url:
            self.slack_webhook_url = self._load_slack_webhook_from_ssm()
        
        # Initialize AWS SSM client for parameter access
        try:
            self.ssm = boto3.client('ssm', region_name=os.getenv('AWS_REGION', 'ap-south-1'))
        except Exception as e:
            logger.warning(f"Could not initialize SSM client: {e}")
            self.ssm = None
        
        logger.info("Notification manager initialized")
    
    def _load_slack_webhook_from_ssm(self) -> str:
        """Load Slack webhook from AWS SSM Parameter Store if configured."""
        try:
            if self.ssm is None:
                return ""
            
            param_name = "/smartcloudops/dev/slack/webhook"
            resp = self.ssm.get_parameter(Name=param_name, WithDecryption=True)
            self.slack_webhook_url = resp.get("Parameter", {}).get("Value", "")
            if self.slack_webhook_url:
                logger.info(f"Loaded Slack webhook from SSM parameter: {param_name}")
            else:
                logger.warning("Slack webhook not found in SSM parameter response")
        except Exception as e:
            logger.warning(f"Could not load Slack webhook from SSM: {e}")
            self.slack_webhook_url = ""
        
        return self.slack_webhook_url
    
    def send_remediation_notification(self, evaluation: Dict[str, Any], execution_results: List[Dict]) -> Dict[str, Any]:
        """
        Send notification about remediation actions.
        
        Args:
            evaluation: Anomaly evaluation results
            execution_results: Results of executed actions
            
        Returns:
            Dict with notification results
        """
        try:
            if not self.slack_webhook_url:
                logger.warning("No Slack webhook URL configured, skipping notification")
                return {
                    'status': 'skipped',
                    'reason': 'No Slack webhook URL configured'
                }
            
            # Create notification message
            message = self._create_remediation_message(evaluation, execution_results)
            
            # Send to Slack
            response = self._send_slack_message(message)
            
            return {
                'status': 'success' if response.get('ok') else 'error',
                'slack_response': response,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error sending remediation notification: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _create_remediation_message(self, evaluation: Dict[str, Any], execution_results: List[Dict]) -> Dict[str, Any]:
        """Create a formatted Slack message for remediation notification."""
        try:
            severity = evaluation.get('severity', 'unknown')
            anomaly_score = evaluation.get('anomaly_score', 0)
            issues = evaluation.get('issues', [])
            
            # Determine color based on severity
            color_map = {
                'critical': '#ff0000',  # Red
                'high': '#ff6600',      # Orange
                'medium': '#ffcc00',    # Yellow
                'low': '#00cc00',       # Green
                'normal': '#cccccc'     # Gray
            }
            color = color_map.get(severity, '#cccccc')
            
            # Create fields for the message
            fields = []
            
            # Anomaly details
            fields.append({
                'title': 'Anomaly Score',
                'value': f"{anomaly_score:.3f}",
                'short': True
            })
            
            fields.append({
                'title': 'Severity',
                'value': severity.upper(),
                'short': True
            })
            
            # Issues
            if issues:
                fields.append({
                    'title': 'Detected Issues',
                    'value': ', '.join(issues),
                    'short': False
                })
            
            # Action results
            if execution_results:
                action_summary = []
                for result in execution_results:
                    action = result.get('action', {})
                    action_type = action.get('action', 'unknown')
                    status = result.get('result', {}).get('status', 'unknown')
                    action_summary.append(f"• {action_type}: {status}")
                
                fields.append({
                    'title': 'Executed Actions',
                    'value': '\n'.join(action_summary),
                    'short': False
                })
            
            # Create the Slack message
            message = {
                'attachments': [
                    {
                        'color': color,
                        'title': f'🚨 SmartCloudOps Auto-Remediation Alert',
                        'text': f'Anomaly detected and remediation actions executed.',
                        'fields': fields,
                        'footer': 'SmartCloudOps AI',
                        'ts': int(datetime.now().timestamp())
                    }
                ]
            }
            
            return message
            
        except Exception as e:
            logger.error(f"Error creating remediation message: {e}")
            return {
                'text': f'Error creating remediation notification: {str(e)}'
            }
    
    def _send_slack_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send message to Slack webhook."""
        try:
            response = requests.post(
                self.slack_webhook_url,
                json=message,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Slack API error: {response.status_code} - {response.text}")
                return {
                    'ok': False,
                    'error': f'HTTP {response.status_code}: {response.text}'
                }
                
        except Exception as e:
            logger.error(f"Error sending Slack message: {e}")
            return {
                'ok': False,
                'error': str(e)
            }
    
    def send_simple_notification(self, title: str, message: str, severity: str = 'info') -> Dict[str, Any]:
        """
        Send a simple notification.
        
        Args:
            title: Notification title
            message: Notification message
            severity: Severity level (info, warning, error)
            
        Returns:
            Dict with notification results
        """
        try:
            if not self.slack_webhook_url:
                logger.warning("No Slack webhook URL configured, skipping notification")
                return {
                    'status': 'skipped',
                    'reason': 'No Slack webhook URL configured'
                }
            
            # Determine color based on severity
            color_map = {
                'info': '#00cc00',      # Green
                'warning': '#ffcc00',   # Yellow
                'error': '#ff0000'      # Red
            }
            color = color_map.get(severity, '#cccccc')
            
            slack_message = {
                'attachments': [
                    {
                        'color': color,
                        'title': title,
                        'text': message,
                        'footer': 'SmartCloudOps AI',
                        'ts': int(datetime.now().timestamp())
                    }
                ]
            }
            
            response = self._send_slack_message(slack_message)
            
            return {
                'status': 'success' if response.get('ok') else 'error',
                'slack_response': response,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error sending simple notification: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of the notification manager."""
        try:
            return {
                'status': 'operational',
                'slack_webhook_configured': bool(self.slack_webhook_url),
                'ssm_available': self.ssm is not None,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting notification status: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
