"""
monitor.py — AWS Resource Monitor
Scans EC2, S3, EBS, and estimates costs using Boto3
"""
import boto3, yaml, json
from datetime import datetime, timedelta
from cost_analyzer import estimate_ec2_cost, estimate_s3_cost
from reporter import generate_report

def load_config(path="config/config.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)

def get_ec2_instances(ec2):
    """Fetch all running EC2 instances with metadata"""
    instances = []
    response = ec2.describe_instances(Filters=[{"Name":"instance-state-name","Values":["running","stopped"]}])
    for r in response["Reservations"]:
        for i in r["Instances"]:
            name = next((t["Value"] for t in i.get("Tags",[]) if t["Key"]=="Name"), "unnamed")
            instances.append({
                "id": i["InstanceId"],
                "name": name,
                "type": i["InstanceType"],
                "state": i["State"]["Name"],
                "launch_time": str(i["LaunchTime"]),
                "region": i.get("Placement",{}).get("AvailabilityZone","unknown")
            })
    return instances

def get_s3_buckets(s3):
    """List all S3 buckets with size estimation"""
    buckets = []
    response = s3.list_buckets()
    for b in response.get("Buckets", []):
        buckets.append({
            "name": b["Name"],
            "created": str(b["CreationDate"]),
        })
    return buckets

def get_idle_instances(cloudwatch, instances, cpu_threshold=5.0):
    """Find EC2 instances with avg CPU < threshold (idle)"""
    idle = []
    end = datetime.utcnow()
    start = end - timedelta(days=7)
    for inst in instances:
        if inst["state"] != "running":
            continue
        metrics = cloudwatch.get_metric_statistics(
            Namespace="AWS/EC2",
            MetricName="CPUUtilization",
            Dimensions=[{"Name":"InstanceId","Value":inst["id"]}],
            StartTime=start, EndTime=end,
            Period=86400, Statistics=["Average"]
        )
        if metrics["Datapoints"]:
            avg_cpu = sum(d["Average"] for d in metrics["Datapoints"]) / len(metrics["Datapoints"])
            if avg_cpu < cpu_threshold:
                inst["avg_cpu_7d"] = round(avg_cpu, 2)
                idle.append(inst)
    return idle

def main():
    cfg = load_config()
    region = cfg["aws"]["region"]
    print(f"🔍 Starting AWS Cloud Monitor | Region: {region}")
    print(f"⏱ {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n")

    ec2 = boto3.client("ec2", region_name=region)
    s3 = boto3.client("s3", region_name=region)
    cw = boto3.client("cloudwatch", region_name=region)

    instances = get_ec2_instances(ec2)
    buckets = get_s3_buckets(s3)
    idle = get_idle_instances(cw, instances, cfg["thresholds"]["idle_cpu_percent"])

    ec2_cost = estimate_ec2_cost(instances)
    s3_cost = estimate_s3_cost(buckets)
    total = round(ec2_cost + s3_cost, 2)

    print(f"📦 EC2 Instances : {len(instances)}")
    print(f"🪣 S3 Buckets    : {len(buckets)}")
    print(f"😴 Idle Instances: {len(idle)}")
    print(f"💰 Est. Monthly  : ${total}")

    report = {
        "timestamp": str(datetime.utcnow()),
        "region": region,
        "instances": instances,
        "buckets": buckets,
        "idle_instances": idle,
        "cost": {"ec2": ec2_cost, "s3": s3_cost, "total": total}
    }

    if total > cfg["thresholds"]["monthly_cost_usd"]:
        print(f"\n⚠️ ALERT: Cost ${total} exceeds threshold ${cfg['thresholds']['monthly_cost_usd']}")

    generate_report(report, cfg["report"]["output_dir"])
    print("\n✅ Monitor run complete.")

if __name__ == "__main__":
    main()
