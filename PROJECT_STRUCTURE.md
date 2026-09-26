# GithubclaudeAI - Project Structure

## 📁 Organized Folder Layout

```
GithubclaudeAI/
│
├── 00_Config/                          # Configuration & Environment
│   ├── vscode/                         # VS Code settings
│   ├── claude/                         # Claude Code configuration
│   └── requirements.txt                # Python dependencies
│
├── 01_DataLayer/                       # Raw Data & Transformations
│   ├── raw_bronze/                     # Raw CSV files from Kaggle
│   │   ├── customer_master.csv
│   │   ├── product_catalog.csv
│   │   ├── order_items.csv
│   │   └── ecommerce_sales_customer_analytics_150k.csv
│   │
│   └── transformed/                    # Transformed parquet files
│       ├── temp_customers.parquet/
│       ├── temp_orders.parquet/
│       ├── temp_products.parquet/
│       ├── temp_sales.parquet/
│       ├── temp_sales_analytics.parquet/
│       ├── temp_customer_analytics.parquet/
│       ├── temp_product_analytics.parquet/
│       └── temp_dataset_statistics.parquet/
│
├── 02_SemanticModel/                   # Semantic Model Definitions
│   ├── schema/                         # Schema documentation
│   │   ├── SCHEMA_DOCUMENTATION.md
│   │   └── semantic_model_schema.md
│   │
│   ├── exports/                        # Exported model definitions
│   │   ├── semantic_model.json         # Complete semantic model (8 tables, 47+ columns)
│   │   └── semantic_model_schema.json
│   │
│   └── definition/                     # Fabric semantic model definitions
│       └── definition.pbism
│
├── 03_Reports/                         # Power BI Reports & Guides
│   ├── guides/                         # Build guides & documentation
│   │   ├── POWER_BI_REPORT_BUILD_GUIDE.md     # Fabric lakehouse edition (v3.0)
│   │   ├── POWER_BI_BUILD_GUIDE.md
│   │   └── gold_layer_transformation.sql
│   │
│   ├── pbix_files/                     # Power BI report files
│   │   ├── Sales & Returns Executive Summary.pbix
│   │   ├── new.pbix
│   │   ├── *.pdf                       # Exported report PDFs
│   │   └── assets/                     # Report-related assets
│   │
│   └── definition/                     # Fabric report definitions
│       └── definition.pbir
│
├── 04_Documentation/                   # Project Documentation
│   ├── setup/                          # Setup & Configuration
│   │   └── FABRIC_CONNECTION_SETUP.md  # Complete Fabric setup guide
│   │
│   ├── status/                         # Project Status Reports
│   │   └── PROJECT_STATUS_v2.0.md      # Current project status
│   │
│   └── guides/                         # Technical Guides
│       ├── Data transformation guides
│       └── Integration guides
│
├── 05_Scripts/                         # Python Scripts & Notebooks
│   ├── pipelines/                      # Data pipelines
│   │   ├── medallion_pipeline.py       # Main medallion architecture (Bronze→Silver→Gold)
│   │   └── run_medallion_pipeline.py   # Pipeline orchestrator
│   │
│   ├── fabric_mcp/                     # Fabric MCP Server Integration
│   │   ├── custom_fabric_mcp_server.py # Custom MCP server for Fabric
│   │   └── read_semantic_model_vscode.py  # VS Code auth helper
│   │
│   ├── notebooks/                      # Jupyter Notebooks
│   │   ├── fabric_setup_notebook.ipynb    # Fabric setup & configuration
│   │   ├── medallion_medallion_pipeline.ipynb
│   │   └── *.ipynb                     # Analysis & exploration notebooks
│   │
│   └── utilities/                      # Helper scripts
│       ├── check_lakehouse_contents.py # Verify lakehouse data
│       └── auto_build_power_bi_report.py
│
├── 06_Assets/                          # Images & Resources
│   └── images/                         # UI icons and screenshots
│       ├── calendar_month_24dp.png
│       ├── globe_24dp.png
│       ├── shopping_cart_24dp.png
│       ├── new_page-001.jpg            # Report previews
│       └── *.png                       # Other assets
│
├── .vscode/                            # VS Code Configuration
│   ├── settings.json                   # VS Code settings
│   └── mcp.json                        # MCP server configuration
│
├── .claude/                            # Claude Code Configuration
│   ├── CLAUDE.md                       # Project instructions
│   └── settings.local.json             # Local settings
│
├── README.md                           # Main project readme
├── PROJECT_STRUCTURE.md                # This file
├── LICENSE                             # MIT License
│
└── delta/                              # Delta Lake tables (local storage)
    ├── customers/
    ├── orders/
    ├── products/
    └── sales/
```

---

## 📊 Data Flow

```
Raw Data (01_DataLayer/raw_bronze/)
        ↓
    Kaggle CSV Files
        ↓
Medallion Pipeline (05_Scripts/pipelines/)
        ↓
Transform to Parquet (01_DataLayer/transformed/)
        ↓
Fabric Lakehouse (githubclaude)
        ↓
Semantic Model (02_SemanticModel/)
        ↓
Power BI Reports (03_Reports/)
```

---

## 🎯 Key Components

### 1. **Data Layer (01_DataLayer/)**
- **raw_bronze/**: Original CSV files from Kaggle
- **transformed/**: Parquet files after medallion transformation
- Data quality: 81.9% of columns have zero nulls
- Total rows: 338,292 (138K orders, 25K customers, 1.2K products)

### 2. **Semantic Model (02_SemanticModel/)**
- **8 tables** with 47+ columns
- **180+ total columns** across all tables
- Complete schema documentation
- JSON exports for Power BI integration

### 3. **Reports (03_Reports/)**
- Power BI Build Guide (v3.0 - Fabric edition)
- Complete with DAX measures, slicers, and visualizations
- 5-page interactive dashboard structure

### 4. **Documentation (04_Documentation/)**
- Fabric connection setup guide
- Project status reports
- Technical guides and references

### 5. **Scripts (05_Scripts/)**
- **Pipelines**: Medallion architecture implementation
- **Fabric MCP**: Custom MCP server for Claude Code integration
- **Notebooks**: Jupyter for exploration and analysis
- **Utilities**: Helper scripts for verification and automation

### 6. **Assets (06_Assets/)**
- UI icons and report screenshots
- Images for documentation

---

## 🚀 Quick Start

### 1. **Setup Environment**
```bash
cd 00_Config
pip install -r requirements.txt
```

### 2. **Explore Data**
```bash
python 05_Scripts/utilities/check_lakehouse_contents.py
```

### 3. **Run Pipeline**
```bash
python 05_Scripts/pipelines/medallion_pipeline.py
```

### 4. **View Semantic Model**
```bash
cat 02_SemanticModel/exports/semantic_model.json
```

### 5. **Build Power BI Report**
See `03_Reports/guides/POWER_BI_REPORT_BUILD_GUIDE.md`

---

## 📋 File Summary

| Category | Count | Purpose |
|----------|-------|---------|
| **Documentation** | 8 files | Setup guides, status, technical docs |
| **Scripts** | 7 files | Pipelines, utilities, MCP server |
| **Notebooks** | 3 files | Analysis, setup, exploration |
| **Data Files** | 15+ files | Raw CSV, transformed parquet |
| **Reports** | 3+ files | PBIX files, PDFs, guides |
| **Configuration** | 4 files | VS Code, Claude Code, requirements |

---

## 🔄 Medallion Architecture

```
Bronze Layer: Raw data from Kaggle
  ↓
Silver Layer: Cleaned & transformed (parquet)
  ↓
Gold Layer: Business-ready analytics tables
  ↓
Semantic Model: 8 tables, 47+ columns, 180+ total columns
  ↓
Power BI: 5-page interactive dashboard
```

---

## 📝 Notes

- **Data Quality**: Excellent - all nulls follow expected business logic
- **Fabric Integration**: Complete with MCP server for Claude Code
- **Power BI Ready**: Build guide includes 40+ DAX measures
- **Documentation**: Comprehensive setup and usage guides

---

**Last Updated:** 2026-09-26  
**Project Status:** Production Ready ✅
