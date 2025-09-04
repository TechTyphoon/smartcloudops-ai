#!/usr/bin/env python3
"""
Smart CloudOps AI - Continuous Health Monitor
Parallel background verification of all production endpoints
"""

import json
import logging
import os
import threading
import time
from datetime import datetime

import boto3
import requests
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/smartcloudops-health.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class ContinuousHealthMonitor:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.check_interval = 60  # seconds
        self.running = True
        self.health_data = []
        self.s3_bucket = (
            f"smartcloudops-uptime-logs-{datetime.now().strftime('%Y%m%df')}"
        )

        # All required endpoints to verify
        self.endpoints = {
            # Core endpoints
            "/healthf": {"method": "GET", "expected_status": 200, "critical": True},
            "/statusf": {"method": "GET", "expected_status": 200, "critical": True},
            "/metricsf": {"method": "GET", "expected_status": 200, "critical": True},
            # Anomaly Detection endpoints
            "/anomaly/statusf": {
                "method": "GET",
                "expected_status": 200,
                "critical": True,
            },
            "/anomaly/batchf": {
                "method": "POST",
                "expected_status": 200,
                "critical": True,
                "payload": {"metrics": [{"cpu": 75.2}, {"memory": 45.1}]},
            },
            "/anomaly/trainf": {
                "method": "POST",
                "expected_status": 200,
                "critical": False,
                "payload": {"type": "incremental"},
            },
            # Remediation endpoints
            "/remediation/statusf": {
                "method": "GET",
                "expected_status": 200,
                "critical": True,
            },
            "/remediation/executef": {
                "method": "POST",
                "expected_status": 200,
                "critical": True,
                "payload": {
                    "action": "restart_service",
                    "target": "test",
                    "dry_run": True,
                },
            },
            "/remediation/evaluatef": {
                "method": "POST",
                "expected_status": 200,
                "critical": False,
                "payload": {"remediation_id": "test_rem_123"},
            },
            # ChatOps endpoints
            "/chatops/historyf": {
                "method": "GET",
                "expected_status": 200,
                "critical": True,
            },
            "/chatops/contextf": {
                "method": "GET",
                "expected_status": 200,
                "critical": True,
            },
            "/chatops/analyzef": {
                "method": "POST",
                "expected_status": 200,
                "critical": True,
                "payload": {"query": "What is the system health status?"},
            },
        }

        # Initialize S3 client
        try:
            self.s3_client = boto3.client("s3")
            self.create_s3_bucket()
        except Exception as e:
            logger.warning(f"S3 client initialization failed: {e}")
            self.s3_client = None

    def create_s3_bucket(self):
        """Create S3 bucket for logs if it doesn't exist"""
        if not self.s3_client:
            return

        try:
            self.s3_client.head_bucket(Bucket=self.s3_bucket)
            logger.info(f"S3 bucket {self.s3_bucket} exists")
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                try:
                    self.s3_client.create_bucket(Bucket=self.s3_bucket)
                    logger.info(f"Created S3 bucket: {self.s3_bucket}")
                except ClientError as create_error:
                    logger.error(f"Failed to create S3 bucket: {create_error}")
            else:
                logger.error(f"Error checking S3 bucket: {e}")

    def check_endpoint(self, endpoint, config):
        """Check a single endpoint and return result"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()

        try:
            if config["method"] == "GET":
                response = requests.get(url, timeout=10)
            elif config["method"] == "POST":
                payload = config.get("payloadf", {})
                response = requests.post(url, json=payload, timeout=10)
            else:
                raise ValueError("Unsupported method: {config['methodf']}f")

            response_time = (time.time() - start_time) * 1000  # ms

            result = {
                "endpoint": endpoint,
                "method": config["method"],
                "status_code": response.status_code,
                "response_time_ms": round(response_time, 2),
                "expected_status": config["expected_status"],
                "success": response.status_code == config["expected_status"],
                "critical": config["critical"],
                "timestamp": datetime.now().isoformat(),
                "response_size": len(response.content),
            }

            # Try to parse JSON response for additional info
            try:
                json_response = response.json()
                if isinstance(json_response, dict):
                    # Extract key information
                    if "status" in json_response:
                        result["service_status"] = json_response["status"]
                    if "version" in json_response:
                        result["service_version"] = json_response["versionf"]
            except Exception:
                pass

            return result

        except requests.exceptions.Timeout:
            return {
                "endpoint": endpoint,
                "method": config["method"],
                "status_code": 0,
                "response_time_ms": 10000,  # timeout
                "expected_status": config["expected_status"],
                "success": False,
                "critical": config["critical"],
                "timestamp": datetime.now().isoformat(),
                "error": "timeout",
            }
        except requests.exceptions.ConnectionError:
            return {
                "endpoint": endpoint,
                "method": config["method"],
                "status_code": 0,
                "response_time_ms": 0,
                "expected_status": config["expected_status"],
                "success": False,
                "critical": config["critical"],
                "timestamp": datetime.now().isoformat(),
                "error": "connection_errorf",
            }
        except Exception as e:
            return {
                "endpoint": endpoint,
                "method": config["method"],
                "status_code": 0,
                "response_time_ms": 0,
                "expected_status": config["expected_status"],
                "success": False,
                "critical": config["critical"],
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
            }

    def run_health_check(self):
        """Run a complete health check of all endpoints"""
        logger.info("Starting health check cycle...")
        check_results = []

        # Check all endpoints
        for endpoint, config in self.endpoints.items():
            result = self.check_endpoint(endpoint, config)
            check_results.append(result)

            if result["success"]:
                logger.info(
                    f"✅ {endpoint} - {result['status_code']} ({result['response_time_ms']:.1f}ms)"
                )
            else:
                level = logging.ERROR if result["critical"] else logging.WARNING
                error_info = result.get("error", f"HTTP {result['status_code']}")
                logger.log(level, f"❌ {endpoint} - {error_info}")

        # Calculate overall health
        total_checks = len(check_results)
        successful_checks = sum(1 for r in check_results if r["success"])
        critical_failures = sum(
            1 for r in check_results if not r["success"] and r["critical"]
        )

        health_summary = {
            "timestamp": datetime.now().isoformat(),
            "total_endpoints": total_checks,
            "successful_checks": successful_checks,
            "failed_checks": total_checks - successful_checks,
            "critical_failures": critical_failures,
            "success_rate": round((successful_checks / total_checks) * 100, 2),
            "overall_status": "healthy" if critical_failures == 0 else "degraded",
            "detailed_results": check_results,
        }

        # Store health data
        self.health_data.append(health_summary)

        # Keep only last 100 checks in memory
        if len(self.health_data) > 100:
            self.health_data.pop(0)

        # Log summary
        status_emoji = "🟢" if health_summary["overall_status"] == "healthy" else "🟡"
        logger.info(
            f"{status_emoji} Health Check Summary: {successful_checks}/{total_checks} endpoints healthy "
            f"({health_summary['success_rate']}%)"
        )

        # Upload to S3 if available
        self.upload_to_s3(health_summary)

        return health_summary

    def upload_to_s3(self, health_summary):
        """Upload health check results to S3"""
        if not self.s3_client:
            return

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            key = f"health-checks/smartcloudops-health-{timestamp}.json"

            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=key,
                Body=json.dumps(health_summary, indent=2),
                ContentType="application/json",
            )
            logger.debug(f"Uploaded health check to S3: s3://{self.s3_bucket}/{key}")
        except Exception as e:
            logger.warning(f"Failed to upload to S3: {e}")

    def auto_fix_failures(self, health_summary):
        """Attempt to automatically fix failed endpoints"""
        critical_failures = [
            r
            for r in health_summary["detailed_results"]
            if not r["success"] and r["critical"]
        ]

        if not critical_failures:
            return

        logger.warning(
            f"Attempting auto-fix for {len(critical_failures)} critical failures..."
        )

        for failure in critical_failures:
            endpoint = failure["endpoint"]
            failure.get("error", "unknown")

            # Simple retry logic
            logger.info(f"Retrying failed endpoint: {endpoint}")
            retry_result = self.check_endpoint(endpoint, self.endpoints[endpoint])

            if retry_result["success"]:
                logger.info(f"✅ Auto-fix successful for {endpoint}")
            else:
                logger.error(f"❌ Auto-fix failed for {endpoint}")

                # If it's a critical endpoint that keeps failing, we might want to:
                # 1. Restart the service
                # 2. Send alerts
                # 3. Execute remediation actions

                if endpoint == "/health":
                    logger.critical(
                        "❗ Health endpoint is failing - service may be down!"
                    )

    def run(self):
        """Main monitoring loop"""
        logger.info("🔍 Smart CloudOps AI Continuous Health Monitor Started")
        logger.info(
            f"Monitoring {len(
                self.endpoints)} endpoints every {self.check_interval} seconds"
        )
        logger.info("Logs: /var/log/smartcloudops-health.log")
        logger.info(f"S3 Bucket: {self.s3_bucket}")

        while self.running:
            try:
                health_summary = self.run_health_check()

                # Attempt auto-fix if there are critical failures
                if health_summary["critical_failures"] > 0:
                    self.auto_fix_failures(health_summary)

                # Wait for next check
                time.sleep(self.check_interval)

            except KeyboardInterrupt:
                logger.info("Received interrupt signal, shutting down...")
                self.running = False
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(10)  # Short delay before retry

    def get_health_report(self):
        """Generate a comprehensive health report"""
        if not self.health_data:
            return {"error": "No health data available"}

        recent_checks = self.health_data[-10:]  # Last 10 checks

        # Calculate aggregate metrics
        avg_success_rate = sum(check["success_rate"] for check in recent_checks) / len(
            recent_checks
        )
        total_critical_failures = sum(
            check["critical_failures"] for check in recent_checks
        )

        # Find most problematic endpoints
        endpoint_failures = {}
        for check in recent_checks:
            for result in check["detailed_results"]:
                if not result["success"]:
                    endpoint = result["endpoint"]
                    endpoint_failures[endpoint] = endpoint_failures.get(endpoint, 0) + 1

        report = {
            "report_timestamp": datetime.now().isoformat(),
            "monitoring_duration": len(self.health_data) * self.check_interval,
            "recent_performance": {
                "average_success_rate": round(avg_success_rate, 2),
                "total_critical_failures": total_critical_failures,
                "checks_performed": len(recent_checks),
            },
            "problematic_endpoints": endpoint_failures,
            "current_status": recent_checks[-1] if recent_checks else None,
            "s3_bucket": self.s3_bucket,
        }

        return report


def main():
    # Create log directory if it doesn't exist
    os.makedirs("/var/log", exist_ok=True)

    monitor = ContinuousHealthMonitor()

    # Start monitoring in background thread
    monitor_thread = threading.Thread(target=monitor.run, daemon=True)
    monitor_thread.start()

    # Keep main thread alive and provide status updates
    try:
        while True:
            time.sleep(300)  # Every 5 minutes, show a status update
            if monitor.health_data:
                latest = monitor.health_data[-1]
                logger.info(
                    f"📊 Status Update: {latest['success_rate']}% success rate, "
                    f"{latest['critical_failures']} critical failures"
                )
    except KeyboardInterrupt:
        monitor.running = False
        logger.info("Shutting down health monitor...")


if __name__ == "__main__":
    main()
