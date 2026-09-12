# E-Commerce Analytics Semantic Model - Schema Documentation

## Overview
Complete Star Schema semantic model for comprehensive e-commerce analytics with medallion architecture (Bronze→Silver→Gold layers). The model contains 5 tables with 3 relationships and 32+ DAX measures organized across 6 categories.

---

## Table Definitions

### 1. **DimCustomer** (Customer Dimension)
**Source:** `transformed_silver/customer_master.csv`  
**Rows:** 25,000 | **Columns:** 11

| Column | DataType | Description | Format |
|--------|----------|-------------|--------|
| customer_id | String (PK) | Unique customer identifier | - |
| customer_name | String | Full name of customer | - |
| customer_age | Int64 | Age of customer | 0 |
| gender | String | Customer gender (M/F) | - |
| customer_segment | String | Customer segment (Premium/Regular) | - |
| customer_city | String | City of residence | - |
| customer_state | String | State/Province of residence | - |
| customer_country | String | Country of residence | - |
| region | String | Geographic region | - |
| customer_postal_code | String | Postal code | - |
| customer_acquisition_cost | Double | CAC spent on acquisition | $#,##0.00 |

**Key Metrics:**
- Premium Customers: Distinct count of Premium segment
- Regular Customers: Distinct count of Regular segment
- Customer Acquisition Cost Avg: Average CAC

---

### 2. **DimProduct** (Product Dimension)
**Source:** `transformed_silver/product_catalog.csv`  
**Rows:** 1,175 | **Columns:** 9

| Column | DataType | Description | Format |
|--------|----------|-------------|--------|
| product_id | String (PK) | Unique product identifier | - |
| product_name | String | Product name | - |
| product_category | String | Primary category | - |
| product_subcategory | String | Subcategory | - |
| brand | String | Brand name | - |
| supplier | String | Supplier name | - |
| unit_price | Double | Selling price per unit | $#,##0.00 |
| product_cost | Double | Cost per unit | $#,##0.00 |
| product_rating | Double | Product quality rating (0-5) | 0.0 |

**Key Metrics:**
- Total Products: Distinct product count
- Products Sold: Count of products with sales
- Average Product Rating: Mean rating across products
- High Rated Products: Count where rating ≥ 4.0

---

### 3. **DimDate** (Date Dimension)
**Type:** Time Intelligence  
**Range:** 2020-01-01 to 2025-12-31  
**Columns:** 8

| Column | DataType | Description | Format |
|--------|----------|-------------|--------|
| FullDate | DateTime (PK) | Full date | yyyy-mm-dd |
| Year | Int64 | Calendar year | 0 |
| Quarter | String | Quarter (Q1-Q4) | - |
| Month | Int64 | Month number (1-12) | 0 |
| MonthName | String | Month name | - |
| DayOfMonth | Int64 | Day of month (1-31) | 0 |
| DayOfWeek | Int64 | Day of week (1-7) | 0 |
| DayName | String | Day name (Monday, etc.) | - |
| WeekOfYear | Int64 | ISO week number (1-53) | 0 |

**Time Intelligence Measures:**
- YTD Revenue: Year-to-date revenue
- YTD Orders: Year-to-date order count
- MTD Revenue: Month-to-date revenue
- Previous Year Revenue: SAMEPERIODLASTYEAR comparison
- YoY Growth %: Year-over-year growth rate
- Revenue Trend: 30-day rolling average

---

### 4. **FactSales** (Sales Fact Table)
**Source:** `transformed_silver/order_items.csv`  
**Rows:** 138,116 | **Columns:** 11

| Column | DataType | Description | Format |
|--------|----------|-------------|--------|
| order_id | String | Order identifier | - |
| customer_id | String (FK) | Customer reference | - |
| product_id | String (FK) | Product reference | - |
| order_date | DateTime (FK) | Order date | yyyy-mm-dd |
| quantity | Int64 | Units ordered | 0 |
| unit_price | Double | Price per unit | $#,##0.00 |
| discount_percent | Double | Discount applied | 0.00% |
| tax_amount | Double | Tax on order | $#,##0.00 |
| shipping_cost | Double | Shipping charge | $#,##0.00 |
| order_status | String | Status (Completed/Cancelled) | - |
| payment_method | String | Payment type | - |

**Granularity:** One row per order item (multiple items per order possible)

---

### 5. **Measures** (Measure Table)
**Type:** Hidden measure table  
**Measures:** 32 DAX formulas across 6 categories

#### Financial Metrics (8 measures)
- **Total Sales:** `SUMX(FactSales, quantity × unit_price)`
- **Total Revenue:** `SUM(quantity × unit_price × (1-discount) + tax + shipping)`
- **Total Cost:** `SUMX(FactSales, quantity × product_cost)`
- **Gross Profit:** `Total Revenue - Total Cost`
- **Gross Profit Margin %:** `Gross Profit / Total Revenue`
- **Total Discount Amount:** `SUM(quantity × unit_price × discount_percent)`
- **Total Tax Amount:** `SUM(tax_amount)`
- **Total Shipping Cost:** `SUM(shipping_cost)`

#### Order Metrics (8 measures)
- **Total Orders:** `DISTINCTCOUNT(order_id)`
- **Average Order Value:** `Total Revenue / Total Orders`
- **Total Order Items:** `SUM(quantity)`
- **Average Items per Order:** `Total Order Items / Total Orders`
- **Completed Orders:** `COUNTIF(order_status, "Completed")`
- **Cancelled Orders:** `COUNTIF(order_status, "Cancelled")`
- **Order Completion Rate %:** `Completed Orders / Total Orders`

#### Customer Metrics (5 measures)
- **Total Unique Customers:** `DISTINCTCOUNT(customer_id)`
- **Revenue per Customer:** `Total Revenue / Total Unique Customers`
- **Orders per Customer:** `Total Orders / Total Unique Customers`
- **Customer Acquisition Cost Avg:** `AVERAGE(customer_acquisition_cost)`
- **Premium Customers:** `DISTINCTCOUNT(customer_id) where segment="Premium"`
- **Regular Customers:** `DISTINCTCOUNT(customer_id) where segment="Regular"`

#### Product Metrics (5 measures)
- **Total Products:** `DISTINCTCOUNT(product_id)`
- **Products Sold:** `DISTINCTCOUNT(product_id) with sales`
- **Average Product Rating:** `AVERAGE(product_rating)`
- **High Rated Products:** `DISTINCTCOUNT(product_id) where rating≥4`
- **Revenue by Category:** `SUM revenue grouped by category`

#### Quality Metrics (3 measures)
- **Quality Score:** `AVERAGE(product_rating)`
- **Order Defect Rate %:** `Cancelled Orders / Total Orders`
- **Average Discount %:** `AVERAGE(discount_percent)`

#### Time Intelligence (6 measures)
- **YTD Revenue:** `DATESYTD calculation`
- **YTD Orders:** `DATESYTD distinct orders`
- **MTD Revenue:** `DATESMTD calculation`
- **Previous Year Revenue:** `SAMEPERIODLASTYEAR`
- **YoY Growth %:** `(Current - Prior Year) / Prior Year`
- **Revenue Trend:** `30-day rolling calculation`

---

## Relationships

### 1. FK_FactSales_DimCustomer
- **From:** FactSales[customer_id]
- **To:** DimCustomer[customer_id]
- **Cardinality:** Many-to-One
- **Cross Filter:** Both Directions
- **Purpose:** Enables customer segmentation, regional analysis, CAC analysis

### 2. FK_FactSales_DimProduct
- **From:** FactSales[product_id]
- **To:** DimProduct[product_id]
- **Cardinality:** Many-to-One
- **Cross Filter:** Both Directions
- **Purpose:** Enables category analysis, brand performance, supplier analysis, rating distribution

### 3. FK_FactSales_DimDate
- **From:** FactSales[order_date]
- **To:** DimDate[FullDate]
- **Cardinality:** Many-to-One
- **Cross Filter:** Both Directions
- **Purpose:** Enables time intelligence, seasonal analysis, YoY comparisons, trend analysis

---

## Data Lineage

### Bronze Layer (Raw)
- 5 CSV files (83.07 MB, 561,861 rows)
- Source: Kaggle E-Commerce Dataset
- No transformations applied

### Silver Layer (Cleaned)
- 5 CSV files (22.85 MB, 189,203 rows)
- Deduplication: 66.3% reduction (372,658 rows removed)
- Data quality validation applied
- **Files:**
  - `customer_master.csv` (25,000 rows)
  - `product_catalog.csv` (1,175 rows)
  - `order_items.csv` (138,116 rows)
  - `ecommerce_sales_customer_analytics_150k.csv` (24,911 rows)

### Gold Layer (Analytics)
- Semantic model tables (this file)
- Star schema design for BI/Analytics
- 32+ DAX measures for business intelligence

---

## Configuration

| Setting | Value |
|---------|-------|
| Compatibility Level | 1600 |
| Default Culture | en-US |
| Collation | en-US_UTF-8 |
| Data Import Mode | Import (not DirectQuery) |
| File Format | TMDL (Tabular Model Definition Language) |

---

## Usage Notes

1. **Refresh Strategy:** Set up daily/weekly refresh from Silver layer
2. **Aggregate Tables:** Consider materializing high-traffic measures for performance
3. **Row-Level Security:** Can be implemented on DimCustomer or DimProduct tables
4. **Performance:** Star schema optimized for Power BI/Fabric analytics
5. **Scaling:** Fact table designed for 100M+ rows with proper indexing

---

## Related Files

- `definition.tmdl` - Database configuration
- `model.tmdl` - Model and relationship definitions
- `database.tmdl` - Compatibility and culture settings
- `relationships.tmdl` - Detailed relationship configurations
- `tables/*.tmdl` - Individual table definitions
- `cultures/en-US.tmdl` - Display strings and metadata

---

**Last Updated:** 2026-09-12  
**Version:** 1.0  
**Status:** Production Ready
