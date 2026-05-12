"""
s3_auditor.py — Audit S3 buckets for security and cost hygiene
"""
import boto3
import yaml

with open("config/config.yaml") as f:
    CONFIG = yaml.safe_load(f)

REGION = CONFIG["aws"]["region"]

def audit_buckets():
    s3 = boto3.client("s3", region_name=REGION)
    buckets = s3.list_buckets()["Buckets"]
    print(f"🪣 Auditing {len(buckets)} S3 buckets...\n")
    issues = []
    for bucket in buckets:
        name = bucket["Name"]
        flags = []
        try:
            pub = s3.get_public_access_block(Bucket=name)["PublicAccessBlockConfiguration"]
            if not all(pub.get(k, False) for k in ["BlockPublicAcls","BlockPublicPolicy","IgnorePublicAcls","RestrictPublicBuckets"]):
                flags.append("PUBLIC_ACCESS_RISK")
        except Exception:
            flags.append("NO_PUBLIC_ACCESS_BLOCK")
        ver = s3.get_bucket_versioning(Bucket=name)
        if ver.get("Status") != "Enabled":
            flags.append("VERSIONING_DISABLED")
        try:
            s3.get_bucket_encryption(Bucket=name)
        except Exception:
            flags.append("ENCRYPTION_MISSING")
        status = "⚠️ ISSUES" if flags else "✅ OK"
        print(f" {status} {name}")
        if flags:
            print(f" → {', '.join(flags)}")
        issues.append({"bucket": name, "flags": flags})
    print(f"\n📋 Total issues found: {sum(len(i['flags']) for i in issues)}")
    return issues

if __name__ == "__main__":
    audit_buckets()
