"""reporter.py — Generate CSV and HTML cost reports"""
import csv, os
from datetime import datetime

def generate_report(data, output_dir="./reports"):
    os.makedirs(output_dir, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    # CSV
    csv_path = f"{output_dir}/report_{ts}.csv"
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id","name","type","state","avg_cpu_7d"])
        w.writeheader()
        for inst in data["instances"]:
            w.writerow({k: inst.get(k,"") for k in ["id","name","type","state","avg_cpu_7d"]})
    print(f"📄 CSV report: {csv_path}")

    # HTML
    html_path = f"{output_dir}/report_{ts}.html"
    rows = "".join(
        f"<tr><td>{i.get('id','')}</td><td>{i.get('name','')}</td>"
        f"<td>{i.get('type','')}</td><td>{i.get('state','')}</td></tr>"
        for i in data["instances"]
    )
    html = f"""<!DOCTYPE html><html><body>
<h2>AWS Cloud Monitor Report</h2>
<p>Generated: {data['timestamp']} | Region: {data['region']}</p>
<p>EC2: ${data['cost']['ec2']} | S3: ${data['cost']['s3']}</p>
<table border='1'><tr><th>ID</th><th>Name</th><th>Type</th><th>State</th></tr>{rows}</table>
</body></html>"""
    with open(html_path, "w") as f:
        f.write(html)
    print(f"🌐 HTML report: {html_path}")
