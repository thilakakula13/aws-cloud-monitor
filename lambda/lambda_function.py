"""
lambda_function.py — AWS Lambda handler for scheduled cloud monitoring
Deploy via AWS Console or SAM. Trigger: CloudWatch Events (cron)
"""
import json, boto3, os
from datetime import datetime

def lambda_handler(event, context):
    region = os.environ.get("AWS_REGION", "us-east-1")
    threshold = float(os.environ.get("COST_THRESHOLD_USD", "100.0"))
    sns_topic = os.environ.get("SNS_TOPIC_ARN", "")

    ec2 = boto3.client("ec2", region_name=region)
    instances = ec2.describe_instances(Filters=[{"Name":"instance-state-name","Values":["running"]}])
    running_count = sum(len(r["Instances"]) for r in instances["Reservations"])

    message = {
        "timestamp": str(datetime.utcnow()),
        "region": region,
        "running_instances": running_count,
        "status": "Monitor check complete"
    }

    if sns_topic and running_count > 0:
        sns = boto3.client("sns", region_name=region)
        sns.publish(
            TopicArn=sns_topic,
            Subject="☁️ AWS Cloud Monitor Alert",
            Message=json.dumps(message, indent=2)
        )

    print(json.dumps(message))
    return {"statusCode": 200, "body": json.dumps(message)}
