# 🏗️ Medallion Architecture Data Pipeline

E-Commerce Sales and Customer Analytics | Kaggle → Fabric Lakehouse

## 📋 Overview

This pipeline implements the **Medallion Architecture** for data transformation:

```
Kaggle Dataset
    ↓
[BRONZE LAYER] → Raw CSV files
    ↓
[SILVER LAYER] → Cleaned & Standardized Parquet/Delta
    ↓
[GOLD LAYER] → Aggregated Analytics Parquet/Delta
    ↓
Fabric Lakehouse (githubclaude)
```

### Key Features
- ✅ **No Local Exports** - Streams directly to Fabric Lakehouse
- ✅ **Automated Downloads** - Kaggle dataset integrated
- ✅ **Data Quality** - Automatic cleaning, standardization, deduplication
- ✅ **Delta Format** - Query-ready in Fabric SQL Endpoints
- ✅ **Analytics Ready** - Pre-built Gold layer tables
- ✅ **Remote Only** - All processing in cloud/remote storage

---

## 📊 Pipeline Layers

### Bronze Layer (Raw)
- Raw CSV files from Kaggle
- Path: `Files/Bronze/`
- Format: CSV
- Contents:
  - `customers.csv` - Customer information
  - `orders.csv` - Order details
  - `products.csv` - Product catalog
  - `sales.csv` - Sales transactions

### Silver Layer (Cleaned)
- Standardized and cleaned data
- Path: `Files/Silver/`
- Format: Parquet/Delta
- Transformations:
  - Column name standardization (snake_case)
  - Data type conversions
  - Missing value handling
  - Duplicate removal
  - Date parsing

### Gold Layer (Analytics)
- Business-ready analytical tables
- Path: `Files/Gold/`
- Format: Parquet/Delta
- Tables:
  - `customer_analytics.parquet` - Customer metrics & segments
  - `sales_analytics.parquet` - Sales details with product info
  - `product_analytics.parquet` - Product performance metrics

---

## 🚀 Quick Start

### 1. Verify Requirements
```bash
python run_medallion_pipeline.py
```

The script will check:
- ✅ All Python packages installed
- ✅ Kaggle credentials configured
- ✅ Azure/Fabric authentication

### 2. Run Pipeline
```bash
python run_medallion_pipeline.py
```

Expected output:
```
✅ All requirements met!
✅ All credentials configured!
🚀 STARTING PIPELINE
...
✅ PIPELINE EXECUTION COMPLETED SUCCESSFULLY
```

### 3. Access Data in Fabric
1. Open Fabric Portal: https://app.fabric.microsoft.com
2. Navigate to: **Workspace: fabricaena** → **Lakehouse: githubclaude**
3. Browse folders:
   - `Files/Bronze/` - Raw data
   - `Files/Silver/` - Cleaned data
   - `Files/Gold/` - Analytics

---

## 📦 File Structure

```
.
├── run_medallion_pipeline.py          # Main runner
├── medallion_pipeline_remote.py       # Pipeline logic
├── fabric_lakehouse_connector.py      # Fabric integration
├── PIPELINE_README.md                 # This file
└── requirements.txt                   # Python dependencies
```

---

## 🔧 Configuration

### Fabric Configuration
Located in both pipeline files:
```python
TENANT_ID = "30afeb3b-d029-4c64-857b-bb0ad14b9a85"
WORKSPACE_ID = "9c06c853-c4ee-42ad-b784-9ad3c80e7f1d"
LAKEHOUSE_ID = "0b4f9e6c-379c-493f-b707-0c857c8b8041"
LAKEHOUSE_NAME = "githubclaude"
```

### Kaggle Configuration
Requires credentials at: `~/.kaggle/kaggle.json`
```json
{"username":"aenakhichi","key":"KGAT_e61d43dd983f697fbd8a4a5ab8608b1c"}
```

---

## 📊 Data Transformations

### Customer Data
- Remove duplicates (by customer_id)
- Standardize column names
- Convert age to integer
- Handle missing values

### Order Data
- Remove duplicates (by order_id)
- Parse dates
- Convert numeric amounts to float
- Handle missing quantity values

### Product Data
- Remove duplicates (by product_id)
- Standardize column names
- Convert prices to float
- Clean category names

### Sales Data
- Parse all date columns
- Convert amounts and quantities to numeric
- Standardize names
- Handle missing values

---

## 📈 Gold Layer Analytics

### Customer Analytics Table
Columns:
- All customer fields (standardized)
- `total_orders` - Total orders per customer
- `total_spent` - Total revenue per customer
- `avg_order_value` - Average order value

### Sales Analytics Table
Columns:
- All order fields
- `product_name` - Product info merged
- `category` - Product category
- `month` - Order month (derived from date)

### Product Analytics Table
Columns:
- All product fields
- `times_sold` - Total times sold
- `total_quantity` - Total quantity sold

---

## 🔗 Fabric SQL Integration

### Query Bronze Data
```sql
SELECT COUNT(*) as total_customers
FROM delta.`Files/Bronze/customers`
```

### Query Silver Data
```sql
SELECT 
    customer_id,
    age,
    COUNT(*) as purchase_count
FROM delta.`Files/Silver/customers`
GROUP BY customer_id, age
```

### Query Gold Analytics
```sql
SELECT 
    customer_id,
    total_orders,
    total_spent,
    avg_order_value
FROM delta.`Files/Gold/customer_analytics`
WHERE total_spent > 1000
ORDER BY total_spent DESC
```

---

## 🔐 Authentication

### Azure CLI (Recommended)
```bash
az login
az account set --subscription "<subscription-id>"
```

### Interactive Browser
The pipeline will prompt for browser-based authentication if needed.

### Troubleshooting Authentication
```bash
# Check current identity
az account show

# Login with specific tenant
az login --tenant "30afeb3b-d029-4c64-857b-bb0ad14b9a85"

# Clear cached credentials
az logout
```

---

## 📋 Pipeline Execution Flow

```
1. INITIALIZATION
   ├─ Load configuration
   ├─ Connect to Fabric
   └─ Verify lakehouse access

2. BRONZE LAYER (Import)
   ├─ Download Kaggle dataset
   ├─ Read CSV files
   └─ Stream to Files/Bronze/

3. SILVER LAYER (Transform)
   ├─ Load Bronze CSV data
   ├─ Clean & standardize
   ├─ Convert to Parquet/Delta
   └─ Stream to Files/Silver/

4. GOLD LAYER (Aggregate)
   ├─ Load Silver data
   ├─ Create analytics tables
   ├─ Aggregate metrics
   └─ Stream to Files/Gold/

5. COMPLETION
   ├─ Log summary
   ├─ List all files
   └─ Ready for queries
```

---

## 📊 Performance Metrics

### Expected Pipeline Duration
- Small dataset (< 100MB): 2-5 minutes
- Medium dataset (100-500MB): 5-15 minutes
- Large dataset (> 500MB): 15-60 minutes

### File Sizes (Approximate)
- Bronze (CSV): ~50-200 MB
- Silver (Parquet): ~20-80 MB
- Gold (Parquet): ~10-40 MB

---

## 🚨 Troubleshooting

### Issue: "Kaggle credentials not found"
**Solution:**
```bash
# Download from https://www.kaggle.com/settings/account
# Place at ~/.kaggle/kaggle.json
python -c "import kagglehub; kagglehub.dataset_download('datascikhan/e-commerce-sales-and-customer-analytics')"
```

### Issue: "Authentication failed: AADSTS500011"
**Solution:**
```bash
# Lakehouse doesn't have correct permissions or
# You're not in the right tenant
az logout
az login --tenant "30afeb3b-d029-4c64-857b-bb0ad14b9a85"
```

### Issue: "Upload failed to lakehouse"
**Solution:**
```bash
# Verify folder structure exists
# Create manually if needed
mkdir Files/Bronze Files/Silver Files/Gold

# Check permissions
az role assignment list --assignee your-email@company.com
```

### Issue: "No such file or directory: temp_*.parquet"
**Solution:**
- Ensure write permissions in current directory
- Run from directory with write access
- Check disk space (need ~1GB free)

---

## 📝 Logging

Pipeline logs are saved to:
- Console output (real-time)
- `Files/Logs/pipeline_*.log` (in lakehouse)

---

## 🔄 Re-running Pipeline

To clear and re-run:
```bash
# The pipeline will overwrite existing files
# No manual cleanup needed

python run_medallion_pipeline.py
```

---

## 📚 Next Steps

1. **Create SQL Views**
   ```sql
   CREATE VIEW v_customer_analytics AS
   SELECT * FROM delta.`Files/Gold/customer_analytics`
   ```

2. **Build Power BI Dashboard**
   - Connect to Fabric workspace
   - Create new report
   - Select lakehouse tables
   - Design visualizations

3. **Set up Scheduled Refresh**
   - Schedule Python script to run daily
   - Use Fabric scheduled refresh
   - Monitor execution logs

4. **Implement Incremental Load**
   - Modify pipeline for delta detection
   - Only process new files
   - Optimize for performance

---

## 📞 Support

For issues or questions:
1. Check pipeline logs
2. Verify Fabric lakehouse access
3. Confirm Kaggle dataset availability
4. Check Azure authentication

---

## 📄 License

Internal Use Only

---

**Pipeline Version:** 1.0  
**Last Updated:** 2026-08-31  
**Status:** Production Ready ✅
