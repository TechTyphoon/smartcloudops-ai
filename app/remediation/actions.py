import os
import logging
from typing import List, Dict

import boto3
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger(__name__)


class AWSActions:
    """Collection of remediation actions executed via AWS APIs."""

    def __init__(self, region_name: str = None):
        self.region_name = region_name or os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "ap-south-1"))
        self._ec2 = None
        self._ssm = None

    @property
    def ec2(self):
        if not self._ec2:
            self._ec2 = boto3.client("ec2", region_name=self.region_name)
        return self._ec2

    @property
    def ssm(self):
        if not self._ssm:
            self._ssm = boto3.client("ssm", region_name=self.region_name)
        return self._ssm

    def _discover_instances_by_tag(self, tag_key: str, tag_value: str) -> List[str]:
        try:
            reservations = self.ec2.describe_instances(
                Filters=[{"Name": f"tag:{tag_key}", "Values": [tag_value]}, {"Name": "instance-state-name", "Values": ["running"]}]
            )["Reservations"]
            instance_ids: List[str] = []
            for res in reservations:
                for inst in res.get("Instances", []):
                    instance_ids.append(inst["InstanceId"])
            return instance_ids
        except (BotoCoreError, ClientError) as exc:
            logger.error(f"Failed to discover instances by tag {tag_key}={tag_value}: {exc}")
            return []

    def restart_service_via_ssm(self, *, tag_key: str, tag_value: str, service_name: str) -> Dict:
        """Restart a systemd service on instances matching the tag using SSM."""
        instance_ids = self._discover_instances_by_tag(tag_key, tag_value)
        if not instance_ids:
            return {"status": "error", "message": "No instances found for tag filter", "instances": []}

        try:
            commands = [f"sudo systemctl restart {service_name}", f"sudo systemctl is-active {service_name}"]
            response = self.ssm.send_command(
                InstanceIds=instance_ids,
                DocumentName="AWS-RunShellScript",
                Parameters={"commands": commands},
                TimeoutSeconds=60,
            )
            command_id = response.get("Command", {}).get("CommandId", "unknown")
            logger.info(f"Sent SSM restart command {command_id} to instances: {instance_ids}")
            return {"status": "success", "command_id": command_id, "instances": instance_ids}
        except (BotoCoreError, ClientError) as exc:
            logger.error(f"SSM command failed: {exc}")
            return {"status": "error", "message": str(exc), "instances": instance_ids}
