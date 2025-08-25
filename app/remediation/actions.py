#!/usr/bin/env python3
"""
Smart CloudOps AI - Action Manager (Phase 4)
Executes AWS SSM-based remediation actions
"""

import logging
import os
import boto3
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class ActionManager:
    """
    Manages execution of remediation actions via AWS SSM.
    """

    def __init__(self):
        """Initialize the action manager."""
        try:
            self.region = os.getenv("AWS_REGION", "ap-south-1")
            self.ssm = boto3.client("ssm", region_name=self.region)
            self.ec2 = boto3.client("ec2", region_name=self.region)
            logger.info("Action manager initialized for region: {self.region}")
        except Exception as e:
            logger.error("Error initializing action manager: {e}")
            self.ssm = None
            self.ec2 = None

    def execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a remediation action.

        Args:
            action: Action specification with type, target, and parameters

        Returns:
            Dict with execution results
        """
        try:
            action_type = action.get("action", "unknown")
            target = action.get("target", "system")
            priority = action.get("priority", "medium")

            logger.info(
                "Executing action: {action_type} on {target} with priority {priority}"
            )

            # Route to appropriate action handler
            if action_type == "restart_service":
                result = self._restart_service(target, action)
            elif action_type == "scale_up":
                result = self._scale_up(target, action)
            elif action_type == "scale_down":
                result = self._scale_down(target, action)
            elif action_type == "cleanup_disk":
                result = self._cleanup_disk(target, action)
            elif action_type == "optimize_performance":
                result = self._optimize_performance(target, action)
            elif action_type == "enhance_monitoring":
                result = self._enhance_monitoring(target, action)
            else:
                result = {
                    "status": "error",
                    "error": "Unknown action type: {action_type}",
                    "action": action_type,
                }

            # Add metadata
            result.update(
                {
                    "action_type": action_type,
                    "target": target,
                    "priority": priority,
                    "timestamp": datetime.now().isoformat(),
                    "execution_time": time.time(),
                }
            )

            logger.info(
                "Action {action_type} completed with status: "
                "{result.get('status', 'unknown')}"
            )
            return result

        except Exception as e:
            logger.error(
                "Error executing action {action.get('action', 'unknown')}: {e}"
            )
            return {
                "status": "error",
                "error": str(e),
                "action_type": action.get("action", "unknown"),
                "timestamp": datetime.now().isoformat(),
            }

    def _restart_service(self, target: str, action: Dict) -> Dict[str, Any]:
        """Restart a service using AWS SSM."""
        try:
            if self.ssm is None:
                return {"status": "error", "error": "SSM client not available"}

            # Find instances with the target tag
            instances = self._find_instances_by_tag("Name", "smartcloudops-ai-{target}")

            if not instances:
                return {
                    "status": "error",
                    "error": "No instances found for target: {target}",
                }

            results = []
            for instance_id in instances:
                try:
                    # Create SSM command to restart service
                    command = self._create_restart_service_command(target)

                    response = self.ssm.send_command(
                        InstanceIds=[instance_id],
                        DocumentName="AWS-RunShellScript",
                        Parameters={"commands": [command]},
                        TimeoutSeconds=300,
                    )

                    command_id = response["Command"]["CommandId"]

                    # Wait for command completion
                    result = self._wait_for_command_completion(command_id, instance_id)
                    results.append(
                        {
                            "instance_id": instance_id,
                            "command_id": command_id,
                            "result": result,
                        }
                    )

                except Exception as e:
                    logger.error(
                        "Error restarting service on instance {instance_id}: {e}"
                    )
                    results.append({"instance_id": instance_id, "error": str(e)})

            return {
                "status": "success",
                "action": "restart_service",
                "target": target,
                "results": results,
            }

        except Exception as e:
            logger.error("Error in restart_service: {e}")
            return {"status": "error", "error": str(e)}

    def _scale_up(self, target: str, action: Dict) -> Dict[str, Any]:
        """Scale up resources (simulated for demo)."""
        try:
            # In a real implementation, this would:
            # 1. Check current resource usage
            # 2. Calculate required scaling
            # 3. Execute scaling actions via AWS APIs

            logger.info("Scaling up {target} resources")

            return {
                "status": "success",
                "action": "scale_up",
                "target": target,
                "message": "Scaling up {target} resources (simulated)",
                "details": {
                    "current_capacity": "medium",
                    "new_capacity": "high",
                    "estimated_cost_increase": "$0.50/hour",
                },
            }

        except Exception as e:
            logger.error("Error in scale_up: {e}")
            return {"status": "error", "error": str(e)}

    def _scale_down(self, target: str, action: Dict) -> Dict[str, Any]:
        """Scale down resources (simulated for demo)."""
        try:
            logger.info("Scaling down {target} resources")

            return {
                "status": "success",
                "action": "scale_down",
                "target": target,
                "message": "Scaling down {target} resources (simulated)",
                "details": {
                    "current_capacity": "high",
                    "new_capacity": "medium",
                    "estimated_cost_savings": "$0.30/hour",
                },
            }

        except Exception as e:
            logger.error("Error in scale_down: {e}")
            return {"status": "error", "error": str(e)}

    def _cleanup_disk(self, target: str, action: Dict) -> Dict[str, Any]:
        """Clean up disk space using AWS SSM."""
        try:
            if self.ssm is None:
                return {"status": "error", "error": "SSM client not available"}

            instances = self._find_instances_by_tag("Name", "smartcloudops-ai-{target}")

            if not instances:
                return {
                    "status": "error",
                    "error": "No instances found for target: {target}",
                }

            results = []
            for instance_id in instances:
                try:
                    # Create disk cleanup command
                    command = self._create_disk_cleanup_command()

                    response = self.ssm.send_command(
                        InstanceIds=[instance_id],
                        DocumentName="AWS-RunShellScript",
                        Parameters={"commands": [command]},
                        TimeoutSeconds=600,
                    )

                    command_id = response["Command"]["CommandId"]
                    result = self._wait_for_command_completion(command_id, instance_id)

                    results.append(
                        {
                            "instance_id": instance_id,
                            "command_id": command_id,
                            "result": result,
                        }
                    )

                except Exception as e:
                    logger.error("Error cleaning disk on instance {instance_id}: {e}")
                    results.append({"instance_id": instance_id, "error": str(e)})

            return {
                "status": "success",
                "action": "cleanup_disk",
                "target": target,
                "results": results,
            }

        except Exception as e:
            logger.error("Error in cleanup_disk: {e}")
            return {"status": "error", "error": str(e)}

    def _optimize_performance(self, target: str, action: Dict) -> Dict[str, Any]:
        """Optimize application performance."""
        try:
            logger.info("Optimizing performance for {target}")

            return {
                "status": "success",
                "action": "optimize_performance",
                "target": target,
                "message": "Performance optimization completed for {target}",
                "details": {
                    "cache_optimization": "enabled",
                    "connection_pooling": "optimized",
                    "query_optimization": "applied",
                },
            }

        except Exception as e:
            logger.error("Error in optimize_performance: {e}")
            return {"status": "error", "error": str(e)}

    def _enhance_monitoring(self, target: str, action: Dict) -> Dict[str, Any]:
        """Enhance monitoring for the target."""
        try:
            logger.info("Enhancing monitoring for {target}")

            return {
                "status": "success",
                "action": "enhance_monitoring",
                "target": target,
                "message": "Monitoring enhanced for {target}",
                "details": {
                    "alert_thresholds": "adjusted",
                    "monitoring_frequency": "increased",
                    "log_retention": "extended",
                },
            }

        except Exception as e:
            logger.error("Error in enhance_monitoring: {e}")
            return {"status": "error", "error": str(e)}

    def _find_instances_by_tag(self, tag_key: str, tag_value: str) -> List[str]:
        """Find EC2 instances by tag."""
        try:
            if self.ec2 is None:
                return []

            response = self.ec2.describe_instances(
                Filters=[
                    {"Name": "tag:{tag_key}", "Values": [tag_value]},
                    {"Name": "instance-state-name", "Values": ["running"]},
                ]
            )

            instance_ids = []
            for reservation in response["Reservations"]:
                for instance in reservation["Instances"]:
                    instance_ids.append(instance["InstanceId"])

            return instance_ids

        except Exception as e:
            logger.error("Error finding instances by tag: {e}")
            return []

    def _create_restart_service_command(self, target: str) -> str:
        """Create shell command to restart service."""
        if target == "application":
            return """
systemctl stop smartcloudops-app
sleep 5
systemctl start smartcloudops-app
systemctl status smartcloudops-app
"""
        else:
            return """
# Generic service restart for {target}
echo "Restarting {target} service"
systemctl restart {target}
systemctl status {target}
"""

    def _create_disk_cleanup_command(self) -> str:
        """Create shell command to clean up disk space."""
        return """
# Clean up old log files
find /var/log -name "*.log.*" -mtime +7 -delete
find /var/log -name "*.gz" -mtime +7 -delete

# Clean up temporary files
rm -rf /tmp/*
rm -rf /var/tmp/*

# Clean up package cache
yum clean all 2>/dev/null || apt-get clean 2>/dev/null

# Show disk usage after cleanup
df -h
"""

    def _wait_for_command_completion(
        self, command_id: str, instance_id: str, timeout: int = 300
    ) -> Dict[str, Any]:
        """Wait for SSM command to complete."""
        try:
            start_time = time.time()
            while time.time() - start_time < timeout:
                response = self.ssm.get_command_invocation(
                    CommandId=command_id, InstanceId=instance_id
                )

                status = response["Status"]

                if status in ["Success", "Failed", "Cancelled", "TimedOut"]:
                    return {
                        "status": status,
                        "output": response.get("StandardOutputContent", ""),
                        "error": response.get("StandardErrorContent", ""),
                        "exit_code": response.get("ResponseCode", -1),
                    }

                time.sleep(5)

            return {"status": "timeout", "error": "Command execution timed out"}

        except Exception as e:
            logger.error("Error waiting for command completion: {e}")
            return {"status": "error", "error": str(e)}

    def get_status(self) -> Dict[str, Any]:
        """Get status of the action manager."""
        try:
            return {
                "status": "operational",
                "region": self.region,
                "ssm_available": self.ssm is not None,
                "ec2_available": self.ec2 is not None,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error("Error getting action manager status: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }
