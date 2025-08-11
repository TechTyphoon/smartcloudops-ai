import json
import os
import urllib.request
import boto3


def handler(event, context):
  try:
    secret_name = os.environ.get("SLACK_SECRET_NAME")
    region = os.environ.get("AWS_REGION", "us-west-2")
    if not secret_name:
      return {"statusCode": 400, "body": "Missing SLACK_SECRET_NAME"}

    sm = boto3.client("secretsmanager", region_name=region)
    secret_value = sm.get_secret_value(SecretId=secret_name)
    secret_str = secret_value.get("SecretString", "")
    secret = json.loads(secret_str) if secret_str.startswith("{") else {"webhook": secret_str}
    webhook_url = secret.get("webhook") or secret.get("SLACK_WEBHOOK_URL")
    if not webhook_url:
      return {"statusCode": 400, "body": "Webhook not found in secret"}

    # SNS can batch records; post each message
    records = event.get("Records", [])
    for rec in records:
      sns_msg = rec.get("Sns", {}).get("Message", "")
      try:
        msg_json = json.loads(sns_msg)
        alarm_name = msg_json.get("AlarmName", "Alarm")
        reason = msg_json.get("NewStateReason", msg_json.get("Message", ""))
        state = msg_json.get("NewStateValue", "ALARM")
        title = f":rotating_light: {alarm_name} [{state}]"
        payload = {
          "attachments": [
            {
              "color": "#ff0000" if state == "ALARM" else "#ffcc00",
              "title": title,
              "text": reason[:3000],
            }
          ]
        }
      except Exception:
        payload = {"text": f":rotating_light: Alarm: {sns_msg[:3500]}"}

      req = urllib.request.Request(
        webhook_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
      )
      with urllib.request.urlopen(req, timeout=5) as resp:
        resp.read()

    return {"statusCode": 200, "body": "ok"}
  except Exception as e:
    return {"statusCode": 500, "body": str(e)}

