# ☁️ AWS Cloud Cost Monitor — Python + Boto3

> Automated AWS resource monitoring and cost optimization tool using Python, Boto3, and scheduled Lambda alerts.

![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python)
![AWS](https://img.shields.io/badge/AWS-Boto3-orange?logo=amazonaws)
![Lambda](https://img.shields.io/badge/AWS-Lambda-yellow?logo=awslambda)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

## 🚀 Overview
This tool connects to AWS via Boto3 to:
- **Scan** running EC2 instances, S3 buckets, and unused resources
- **Estimate** monthly cost from usage metrics
- **Alert** via SNS when thresholds are breached
- **Generate** a cost report as CSV + HTML
- **Lambda-ready**: deploy as a scheduled CloudWatch Events job

## 📁 Structure
```
aws-cloud-monitor/
├── src/
│   ├── monitor.py          # Main monitoring script
│   ├── cost_analyzer.py    # Cost estimation logic
│   ├── reporter.py         # CSV + HTML report generator
│   ├── ec2_monitor.py      # EC2-specific monitoring
│   ├── s3_auditor.py       # S3 security & cost audit
│   └── alert_manager.py    # SNS alert dispatcher
├── lambda/
│   └── lambda_function.py  # AWS Lambda handler
├── config/
│   └── config.yaml         # Thresholds & settings
├── requirements.txt
└── README.md
```

## ⚙️ Setup
```bash
pip install -r requirements.txt
# Configure AWS credentials
aws configure
# Or set env vars
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1

python src/monitor.py
```

## 🛠️ Tech Stack
`Python` · `Boto3` · `AWS EC2` · `AWS S3` · `AWS Lambda` · `AWS SNS` · `AWS CloudWatch` · `PyYAML`
