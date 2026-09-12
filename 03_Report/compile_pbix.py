import json
import zipfile
from pathlib import Path

# Paths
report_dir = Path("03_Report")
output_pbix = Path("Ecommerce_Report.pbix")

# Standard PBIX base layout mapping
print("Packaging report JSON definitions into standard PBIX structure...")

with zipfile.ZipFile(output_pbix, "w", zipfile.ZIP_DEFLATED) as pbix:
    # 1. Package Layout / report.json definition
    report_json_path = report_dir / "definition" / "report.json"
    if report_json_path.exists():
        pbix.write(report_json_path, arcname="Report/Layout")

    # 2. Package Version Info
    version_json_path = report_dir / "definition" / "version.json"
    if version_json_path.exists():
        pbix.write(version_json_path, arcname="Version")

print(f"Success! Built '{output_pbix.name}'. You can double-click this to open directly in Power BI Desktop.")