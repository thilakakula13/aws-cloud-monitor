"""
ec2_monitor.py — Monitor EC2 instances via CloudWatch
"""
import boto3
import yaml
import datetime
from alert_manager import send_alert

with open("config/config.yaml") as f:
    CONFIG = yaml.safe_load(f)

REGION = CONFIG["aws"]["region"]
CPU_THRESHOLD = CONFIG["thresholds"]["idle_cpu_percent"]
LOOKBACK_MINS = CONFIG.get("lookback_minutes", 10)

def get_all_instances(ec2):
    instances = []
    response = ec2.describe_instances(Filters=[{"Name": "instance-state-name", "Values": ["running"]}])
    for r in response["Reservations"]:
        for i in r["Instances"]:
            name = next((t["Value"] for t in i.get("Tags", []) if t["Key"] == "Name"), i["InstanceId"])
            instances.append({"id": i["InstanceId"], "name": name, "type": i["InstanceType"], "state": i["State"]["Name"]})
    return instances

def get_cpu(cw, instance_id):
    end = datetime.datetime.utcnow()
    start = end - datetime.timedelta(minutes=LOOKBACK_MINS)
    resp = cw.get_metric_statistics(
        Namespace="AWS/EC2",
        MetricName="CPUUtilization",
        Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
        StartTime=start, EndTime=end,
        Period=60, Statistics=["Average"]
    )
    points = sorted(resp["Datapoints"], key=lambda x: x["Timestamp"])
    return points[-1]["Average"] if points else None

def monitor():
    ec2 = boto3.client("ec2", region_name=REGION)
    cw = boto3.client("cloudwatch", region_name=REGION)
    instances = get_all_instances(ec2)
    print(f"🔍 Monitoring {len(instances)} running EC2 instances...\n")
    for inst in instances:
        cpu = get_cpu(cw, inst["id"])
        status = "N/A" if cpu is None else f"{cpu:.1f}%"
        flag = " ⚠️ ALERT" if (cpu or 0) > CPU_THRESHOLD else " ✅"
        print(f" {flag} {inst['name']} ({inst['id']}) | {inst['type']} | CPU: {status}")
        if cpu and cpu > CPU_THRESHOLD:
            send_alert(
                subject=f"[CloudSentinel] HIGH CPU Alert — {inst['id']}",
                message=(
                    f"EC2 Instance {inst['id']} ({inst['name']}) has CPU at {cpu:.1f}%\n"
                    f"Threshold: {CPU_THRESHOLD}% | Region: {REGION}\n"
                    f"Action: Review instance load or consider scaling out."
                )
            )
    print("\n✅ EC2 monitoring scan complete.")

if __name__ == "__main__":
    monitor()
