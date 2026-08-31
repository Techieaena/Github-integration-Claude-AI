"""
Setup Fabric Lakehouse Folder Structure and Upload Files
"""

import os
import json
import shutil
from datetime import datetime

# Configuration
WORKSPACE_ID = "9c06c853-c4ee-42ad-b784-9ad3c80e7f1d"
LAKEHOUSE_ID = "0b4f9e6c-379c-493f-b707-0c857c8b8041"
ABFSS_PATH = f"abfss://Files@onelake.dfs.core.windows.net/{WORKSPACE_ID}/{LAKEHOUSE_ID}/Files"

# Local paths
LOCAL_NOTEBOOK = r"C:\Users\admin\medallion_medallion_pipeline.ipynb"
LOCAL_SQL_SCRIPT = r"C:\Users\admin\gold_layer_transformation.sql"

# Folders to create
FOLDERS = ["Bronze", "Silver", "Gold", "Documentation", "Scripts"]

print("="*80)
print("FABRIC LAKEHOUSE SETUP - Folder Structure & File Upload")
print("="*80)

# Step 1: Display configuration
print("\nConfiguration:")
print(f"  Workspace ID: {WORKSPACE_ID}")
print(f"  Lakehouse ID: {LAKEHOUSE_ID}")
print(f"  ABFSS Path: {ABFSS_PATH}")

# Step 2: Create local staging directory for Fabric files
STAGING_DIR = r"C:\Users\admin\fabric_deployment"
if os.path.exists(STAGING_DIR):
    shutil.rmtree(STAGING_DIR)

os.makedirs(STAGING_DIR, exist_ok=True)
print(f"\n✓ Created staging directory: {STAGING_DIR}")

# Step 3: Create folder structure
print("\nCreating folder structure:")
for folder in FOLDERS:
    folder_path = os.path.join(STAGING_DIR, folder)
    os.makedirs(folder_path, exist_ok=True)
    print(f"  ✓ {folder}/")

# Step 4: Copy notebook to Scripts folder
if os.path.exists(LOCAL_NOTEBOOK):
    dest = os.path.join(STAGING_DIR, "Scripts", "medallion_pipeline.ipynb")
    shutil.copy2(LOCAL_NOTEBOOK, dest)
    print(f"\n✓ Copied notebook to: Scripts/medallion_pipeline.ipynb")
else:
    print(f"\n! Notebook not found: {LOCAL_NOTEBOOK}")

# Step 5: Copy SQL script to Scripts folder
if os.path.exists(LOCAL_SQL_SCRIPT):
    dest = os.path.join(STAGING_DIR, "Scripts", "gold_layer_transformation.sql")
    shutil.copy2(LOCAL_SQL_SCRIPT, dest)
    print(f"✓ Copied SQL script to: Scripts/gold_layer_transformation.sql")
else:
    print(f"! SQL script not found: {LOCAL_SQL_SCRIPT}")

# Step 6: Create README files for each layer
readme_files = {
    "Bronze": """# Bronze Layer - Raw Data

This folder contains raw CSV files imported directly from Kaggle without any transformations.

## Files
- customer_master.csv - Customer master data
- ecommerce_sales_customer_analytics_150k.csv - Main sales dataset (150K records)
- order_items.csv - Order line items and product details
- product_catalog.csv - Product master data
- dataset_statistics.csv - Dataset summary statistics

## Purpose
- Store raw data as-is from source systems
- No transformations or cleaning applied
- Serves as audit trail of original data

## Next Step
Run the medallion_pipeline notebook to transform this data to the Silver layer.
""",

    "Silver": """# Silver Layer - Cleaned & Transformed Data

This folder contains cleaned, deduplicated data with business rule enforcement.

## Transformations Applied
✓ Data type conversions and standardization
✓ Null/missing value handling
✓ Duplicate record removal
✓ Date/time normalization
✓ Referential integrity validation
✓ Business rule enforcement

## Tables (Delta Format)
- customer_silver - Cleaned customer dimension
- sales_silver - Cleaned sales transactions
- order_items_silver - Cleaned order line items
- products_silver - Cleaned product master

## Purpose
- Serve as foundation for analytical models
- Ensure data quality and consistency
- Enable reliable reporting and analysis

## Next Step
Create Gold layer analytical views using the SQL Analytical Endpoint script.
""",

    "Gold": """# Gold Layer - Business Analytics

This folder contains dimensional and fact tables optimized for business analytics.

## Dimensional Tables
- dim_customer - Customer attributes
- dim_product - Product attributes
- dim_date - Date/time attributes

## Fact Tables
- fact_sales - Sales transactions
- fact_order_items - Order line items

## Analytical Views
- customer_segmentation - RFM analysis and customer segments
- sales_by_category - Sales performance by category
- monthly_sales_trend - Monthly revenue trends
- top_products - Best-selling products
- daily_sales_summary - Daily KPI summaries
- customer_lifetime_value - CLV analysis

## Purpose
- Optimized for reporting and dashboards
- Contains aggregations and business metrics
- Supports real-time analytics and Power BI

## Next Step
Connect Power BI to this layer for visualization and dashboarding.
""",

    "Documentation": """# Documentation

This folder contains dataset schema, transformation rules, and pipeline documentation.

## Files
- dataset_schema.md - Complete dataset schema documentation
- README.txt - Comprehensive transformation guide
- schema.json - Schema in JSON format

## Purpose
- Reference for data structure and content
- Transformation methodology documentation
- Data lineage and quality standards

## Usage
Refer to these files for:
- Understanding data structure
- Transformation logic
- Data quality rules
- Troubleshooting and validation
"""
}

print("\nCreating layer documentation:")
for layer, content in readme_files.items():
    readme_path = os.path.join(STAGING_DIR, layer, "README.md")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✓ {layer}/README.md")

# Step 7: Create a deployment summary
summary = {
    "timestamp": datetime.now().isoformat(),
    "workspace_id": WORKSPACE_ID,
    "lakehouse_id": LAKEHOUSE_ID,
    "lakehouse_name": "githubclaude",
    "workspace_name": "fabricaena",
    "folders_created": FOLDERS,
    "files_uploaded": {
        "Scripts": [
            "medallion_pipeline.ipynb",
            "gold_layer_transformation.sql"
        ]
    },
    "status": "Ready for deployment to Fabric"
}

summary_path = os.path.join(STAGING_DIR, "deployment_summary.json")
with open(summary_path, 'w') as f:
    json.dump(summary, f, indent=2)

print(f"\n✓ Created deployment summary: deployment_summary.json")

# Step 8: Display final summary
print("\n" + "="*80)
print("DEPLOYMENT PACKAGE READY")
print("="*80)

print("\nFolder Structure Created:")
for folder in FOLDERS:
    print(f"  📁 {folder}/")
    if folder == "Scripts":
        print(f"     📄 medallion_pipeline.ipynb")
        print(f"     📄 gold_layer_transformation.sql")
    elif folder in readme_files:
        print(f"     📄 README.md")

print(f"\nStaging Directory: {STAGING_DIR}")

print("\n" + "-"*80)
print("NEXT STEPS:")
print("-"*80)

print("""
1. Upload to Fabric Lakehouse:
   - Navigate to: fabricaena workspace → githubclaude lakehouse
   - Upload the staging directory contents to each folder
   - Alternatively, use Azure Storage Explorer to bulk upload

2. Create Fabric Notebook:
   - In githubclaude lakehouse, create new Notebook
   - Copy content from: Scripts/medallion_pipeline.ipynb
   - Name it: "medallion_pipeline"
   - Run all cells sequentially

3. Create SQL Endpoint:
   - In githubclaude lakehouse, create SQL Analytical Endpoint
   - Copy content from: Scripts/gold_layer_transformation.sql
   - Execute to create Gold layer tables

4. Verify Pipeline:
   - Check Bronze folder for raw files
   - Check Silver folder for Delta tables
   - Check Gold folder for analytical tables
   - View Documentation folder for schema and guides

5. Create Power BI Dashboard:
   - Connect to Gold layer tables
   - Create visualizations for business metrics
   - Publish dashboards for stakeholders
""")

print("="*80)
print("✓ Fabric deployment package is ready!")
print("="*80)
