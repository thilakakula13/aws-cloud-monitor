"""
alert_manager.py — SNS-based alert dispatcher
"""
import boto3, yaml

with open("config/config.yaml") as f:
    CONFIG = yaml.safe_load(f)

SNS_ARN = CONFIG["alerts"]["sns_topic_arn"]
REGION = CONFIG["aws"]["region"]

def send_alert(subject: str, message: str):
    sns = boto3.client("sns", region_name=REGION)
    sns.publish(TopicArn=SNS_ARN, Subject=subject, Message=message)
    print(f"🔔 Alert sent: {subject}")
