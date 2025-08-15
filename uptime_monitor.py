#!/usr/bin/env python3
"""
Smart CloudOps AI - 30-Day Uptime Monitor
Tracks uptime and logs to S3 every 5 minutes
"""
import requests
import json
import boto3
from datetime import datetime
import time
import sys

# Service endpoints
SERVICES = {
    "flask_app": "http://44.244.231.27:3000/health",
    "grafana": "http://35.92.147.156:3001",
    "prometheus": "http://35.92.147.156:9090/api/v1/status/config",
}

S3_BUCKET = "smartcloudops-uptime-logs-20250814"


def check_service(name, url):
    """Check if a service is up"""
    try:
        response = requests.get(url, timeout=10)
        return {
            "service": name,
            "status": "UP" if response.status_code == 200 else "DOWN",
            "response_code": response.status_code,
            "response_time": response.elapsed.total_seconds(),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        return {
            "service": name,
            "status": "DOWN",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


def upload_to_s3(data):
    """Upload uptime data to S3"""
    try:
        s3 = boto3.client("s3")
        key = f"uptime-logs/{datetime.utcnow().strftime('%Y/%m/%d/%H%M')}.json"
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=key,
            Body=json.dumps(data),
            ContentType="application/json",
        )
        print(f"Uploaded to s3://{S3_BUCKET}/{key}")
    except Exception as e:
        print(f"S3 upload failed: {e}")


def main():
    """Main monitoring loop"""
    while True:
        try:
            results = []
            for name, url in SERVICES.items():
                result = check_service(name, url)
                results.append(result)
                print(f"{result['timestamp']}: {name} = {result['status']}")

            # Upload to S3
            upload_to_s3(results)

            # Sleep for 5 minutes
            time.sleep(300)

        except KeyboardInterrupt:
            print("Monitoring stopped")
            break
        except Exception as e:
            print(f"Monitor error: {e}")
            time.sleep(60)


if __name__ == "__main__":
    main()
