"""cost_analyzer.py — AWS cost estimation by resource type"""

# Approx on-demand prices (us-east-1, USD/hr)
EC2_PRICES = {
    "t2.micro": 0.0116, "t2.small": 0.023, "t2.medium": 0.0464,
    "t3.micro": 0.0104, "t3.small": 0.0208, "t3.medium": 0.0416,
    "m5.large": 0.096, "m5.xlarge": 0.192, "m5.2xlarge": 0.384,
    "c5.large": 0.085, "c5.xlarge": 0.170,
}

S3_PRICE_PER_GB = 0.023  # Standard storage per GB/month
HOURS_PER_MONTH = 730

def estimate_ec2_cost(instances):
    total = 0.0
    for inst in instances:
        if inst["state"] == "running":
            hourly = EC2_PRICES.get(inst["type"], 0.05)
            total += hourly * HOURS_PER_MONTH
    return round(total, 2)

def estimate_s3_cost(buckets, avg_gb_per_bucket=5.0):
    return round(len(buckets) * avg_gb_per_bucket * S3_PRICE_PER_GB, 2)

def savings_if_idle_stopped(idle_instances):
    savings = 0.0
    for inst in idle_instances:
        hourly = EC2_PRICES.get(inst["type"], 0.05)
        savings += hourly * HOURS_PER_MONTH
    return round(savings, 2)
