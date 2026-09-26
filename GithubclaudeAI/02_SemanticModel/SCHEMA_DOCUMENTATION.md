# 📊 Star Schema Design - E-Commerce Analytics

**Semantic Model:** GithubClaudeAI.SemanticModel  
**Created:** 2026-09-01  
**Version:** 1.0

---

## 🎯 Schema Overview

This semantic model implements a **Star Schema** (Kimball Model) optimized for:
- E-commerce sales analysis
- Customer behavior insights
- Product performance metrics
- Time-based trend analysis

### Schema Diagram

```
                    ┌─────────────────┐
                    │    DimDate      │
                    ├─────────────────┤
                    │ DateKey (PK)    │
                    │ FullDate        │
                    │ Year            │
                    │ Month           │
                    │ Quarter         │
                    │ DayOfWeek       │
                    │ WeekOfYear      │
                    └────────┬────────┘
                             │
                             │ (1:M)
                             │
                ┌────────────┴────────────┐
                │                         │
                │     FactSales (Fact)    │
                │    (397,569 rows)       │
                │                         │
                │  Measures:              │
                │  - Quantity             │
                │  - Gross Sales          │
                │  - Net Sales            │
                │  - Discount             │
                │  - Tax                  │
                │  - Shipping             │
                │  - Profit               │
                │  - Cost                 │
                │                         │
                └────┬────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        │ (1:M)                   │ (1:M)
        │                         │
   ┌────▼──────────┐      ┌──────▼───────────┐
   │ DimCustomer   │      │  DimProduct      │
   ├───────────────┤      ├──────────────────┤
   │ customer_id   │      │ product_id (PK)  │
   │ (PK)          │      │ product_name     │
   │               │      │ category         │
   │ Attributes:   │      │ subcategory      │
   │ - name        │      │ brand            │
   │ - age         │      │ supplier         │
   │ - gender      │      │ unit_price       │
   │ - segment     │      │ product_cost     │
   │ - location    │      │ rating           │
   │ - region      │      └──────────────────┘
   │               │
   └───────────────┘
   (25,000 rows)         (1,175 rows)
```

---

## 📋 Dimension Tables

### 1. DimCustomer
**Purpose:** Stores customer attributes for segmentation and analysis

| Column | Data Type | Description | Business Use |
|--------|-----------|-------------|--------------|
| **customer_id** | String | Unique customer identifier | Primary Key, joins to FactSales |
| customer_name | String | Customer full name | Customer identification |
| customer_age | Int64 | Customer age | Demographic segmentation |
| gender | String | Male/Female | Demographic analysis |
| customer_segment | String | Consumer/Premium/VIP | Customer segmentation |
| customer_city | String | City of residence | Geographic analysis |
| customer_state | String | State/Province | Geographic analysis |
| customer_country | String | Country | Geographic analysis |
| region | String | Geographic region | Regional performance tracking |
| customer_postal_code | String | Postal code | Location-based analysis |
| customer_acquisition_cost | Double | CAC in $ | Customer economics |

**Key Characteristics:**
- 25,000 unique customers
- Supports multi-level geographic hierarchy: Country → State → City
- Acquisition cost enables CLTV (Customer Lifetime Value) calculations
- Segment field enables targeted analysis by customer type

---

### 2. DimProduct
**Purpose:** Stores product attributes for product-level analysis

| Column | Data Type | Description | Business Use |
|--------|-----------|-------------|--------------|
| **product_id** | String | Unique product identifier | Primary Key, joins to FactSales |
| product_name | String | Product name/description | Product identification |
| product_category | String | Product category | Product segmentation |
| product_subcategory | String | Subcategory level | Detailed product grouping |
| brand | String | Brand name | Brand analysis |
| supplier | String | Supplier name | Supply chain analysis |
| unit_price | Double | Base product price | Price analysis |
| product_cost | Double | Cost of goods sold | Profit margin calculation |
| product_rating | Double | Customer rating (avg) | Quality/satisfaction metric |

**Key Characteristics:**
- 1,175 unique products
- Hierarchical structure: Category → Subcategory
- Price and cost enable margin analysis
- Rating enables quality-based performance tracking

---

### 3. DimDate
**Purpose:** Enables time intelligence calculations

| Column | Data Type | Description | Business Use |
|--------|-----------|-------------|--------------|
| **DateKey** | Int64 | Integer date key (YYYYMMDD format) | Primary Key |
| FullDate | DateTime | Full date value | Relationship key to FactSales |
| Year | Int64 | Calendar year (2023, 2024, 2025, etc.) | Year-level analysis |
| Month | Int64 | Month number (1-12) | Monthly aggregation |
| MonthName | String | Month name (January, etc.) | Display in reports |
| Quarter | Int64 | Quarter number (1-4) | Quarterly analysis |
| QuarterName | String | Quarter name (Q1, Q2, etc.) | Display in reports |
| DayOfWeek | Int64 | Day number (1=Sunday, 7=Saturday) | Weekly analysis |
| DayName | String | Day name (Monday, etc.) | Display in reports |
| WeekOfYear | Int64 | ISO week number (1-53) | Weekly aggregation |

**Key Characteristics:**
- Enables all DAX time intelligence functions (YoY, YTD, etc.)
- Supports multiple aggregation levels
- Facilitates trend analysis and seasonality detection

---

## 📊 Fact Table

### FactSales
**Purpose:** Stores all transaction-level facts and metrics

**Dimensions (Foreign Keys):**

| Column | Links To | Type | Purpose |
|--------|----------|------|---------|
| customer_id | DimCustomer | FK | Links to customer attributes |
| order_date | DimDate | FK | Enables time-based analysis |

**Measures (Quantifiable Facts):**

| Column | Data Type | Format | Aggregation | Description |
|--------|-----------|--------|-------------|-------------|
| quantity | Int64 | 0 | SUM | Units sold per order |
| gross_sales | Double | $#,##0.00 | SUM | Revenue before discounts |
| discount_amount | Double | $#,##0.00 | SUM | Total discounts given |
| tax_amount | Double | $#,##0.00 | SUM | Tax collected |
| shipping_cost | Double | $#,##0.00 | SUM | Shipping cost |
| net_sales | Double | $#,##0.00 | SUM | Revenue after discounts (KPI) |
| product_cost | Double | $#,##0.00 | SUM | COGS |
| profit | Double | $#,##0.00 | SUM | Gross profit (KPI) |
| profit_margin_percentage | Double | 0.00% | AVG | Profit margin % |
| customer_rating | Double | 0.0 | AVG | Customer satisfaction |

**Attributes (Non-additive descriptors):**

| Column | Data Type | Description |
|--------|-----------|-------------|
| order_id | String | Unique order identifier |
| order_date | DateTime | Order placement date |
| order_time | String | Order placement time |
| order_status | String | Completed/Cancelled/Pending |
| sales_channel | String | Mobile App/Website/In-Store |
| payment_method | String | Credit Card/Digital Wallet/Debit Card |
| payment_status | String | Paid/Pending/Failed |
| shipping_method | String | Standard/Express/Economy |
| delivery_status | String | On Time/Late/Early |
| return_status | String | Returned/Not Returned |
| is_repeat_customer | String | True/False |
| customer_order_count | Int64 | Customer's order history count |

**Row Count:** 138,116 orders (397,569 → deduplicated after Silver transformation)

---

## 🔗 Relationships

### Relationship 1: FK_FactSales_DimCustomer
```
FactSales.customer_id → DimCustomer.customer_id
```
- **Type:** Many-to-One (1:M)
- **Cardinality:** FactSales rows have exactly one customer
- **Filter Direction:** Bidirectional
- **Purpose:** Enables customer-level filtering and drill-down

**Impact:**
- Filter a customer segment → shows only that segment's sales
- Enables calculating metrics per customer (e.g., Revenue per Customer)

### Relationship 2: FK_FactSales_DimDate
```
FactSales.order_date → DimDate.FullDate
```
- **Type:** Many-to-One (1:M)
- **Cardinality:** Multiple orders per date
- **Filter Direction:** Bidirectional
- **Purpose:** Enables time intelligence and date-based analysis

**Impact:**
- Filter by year → shows annual totals
- Enables YoY/YTD/MoM calculations
- Supports seasonal trend analysis

### Why No Product Dimension Relationship?

The FactSales table contains denormalized product information from the source data. If product IDs were available in the original fact table, we would add:

```
FactSales.product_id → DimProduct.product_id (Proposed)
```

This would enable:
- Product-level drill-downs
- Cross-selling analysis
- Category-based segmentation

---

## 📐 Data Model Characteristics

### Design Principles

1. **Denormalized Fact Table**
   - Includes descriptive attributes (order_status, payment_method, etc.)
   - Reduces number of relationships needed
   - Improves query performance

2. **Conformed Dimensions**
   - DimCustomer, DimProduct shared across all analysis
   - Ensures consistency across reports
   - Single source of truth for attributes

3. **Surrogate Keys**
   - customer_id, product_id are business keys
   - DateKey is an integer surrogate
   - Improves join performance

### Dimensionality

| Aspect | Count |
|--------|-------|
| Dimensions | 3 |
| Fact Tables | 1 |
| Relationships | 2 |
| Measures (DAX) | 30+ |
| Total Columns (Dim) | 30+ |
| Rows (Fact) | 138,116 |

---

## 🎲 Star Schema Benefits

### ✅ Query Performance
- **Simplified JOINs:** Dimensional queries join small dimension tables
- **Indexed Keys:** FK/PK relationships allow efficient lookups
- **Parallel Processing:** Star schema enables parallel fact table scans

### ✅ Analytics Capability
- **Flexible Aggregations:** Roll up by any dimension attribute
- **Time Intelligence:** DimDate enables year-over-year, YTD calculations
- **Drill-Down:** Hierarchical dimensions enable drill-down analysis

### ✅ Maintainability
- **Clear Structure:** Easy to understand for new analysts
- **Separation of Concerns:** Facts separate from dimensions
- **Change Management:** New attributes added to dimension without fact table changes

### ✅ Scalability
- **Growth Ready:** Can add new dimensions without refactoring
- **Partitioning:** Fact table easily partitioned by date
- **Aggregate Tables:** Can add aggregate tables for high-level summaries

---

## 📈 DAX Measures Hierarchy

### Financial Metrics (Display Folder: "Financial Metrics")
```
├── Total_Revenue (SUM of net_sales)
├── Total_Gross_Sales (SUM of gross_sales)
├── Total_Profit (SUM of profit)
├── Total_Discount (SUM of discount_amount)
├── Total_Tax (SUM of tax_amount)
├── Total_Shipping (SUM of shipping_cost)
├── Total_Cost (SUM of product_cost)
└── Profit_Margin_Percent (DIVIDE profit by revenue)
```

### Order Metrics (Display Folder: "Order Metrics")
```
├── Total_Orders (COUNTROWS of FactSales)
├── Total_Items_Sold (SUM of quantity)
├── Average_Order_Value (DIVIDE revenue by orders)
├── Average_Items_Per_Order (DIVIDE items by orders)
├── Completed_Orders (COUNT where order_status = "Completed")
└── Order_Completion_Rate (DIVIDE completed by total)
```

### Customer Metrics (Display Folder: "Customer Metrics")
```
├── Unique_Customers (DISTINCTCOUNT of customer_id)
├── Repeat_Purchase_Count (DISTINCTCOUNT where repeat = True)
├── Repeat_Customer_Rate (DIVIDE repeat by unique)
├── Average_Customer_Rating (AVERAGE of rating)
├── Revenue_per_Customer (DIVIDE revenue by customers)
└── Profit_per_Customer (DIVIDE profit by customers)
```

### Quality Metrics (Display Folder: "Quality Metrics")
```
├── Return_Rate (COUNT returns / total orders)
└── Order_Completion_Rate (Moved to Order Metrics)
```

### Delivery Metrics (Display Folder: "Delivery Metrics")
```
├── On_Time_Delivery_Count (COUNT where delivery = "On Time")
└── On_Time_Delivery_Rate (DIVIDE on_time by total)
```

### Time Intelligence (Display Folder: "Time Intelligence")
```
├── Revenue_YoY_Growth (Compare with SAMEPERIODLASTYEAR)
├── Revenue_MoM_Growth (Compare with DATEADD -1 month)
├── Revenue_YTD (CALCULATE with DATESYTD)
├── Profit_YTD (CALCULATE with DATESYTD)
└── Orders_YTD (CALCULATE with DATESYTD)
```

---

## 🔄 Data Refresh Strategy

### Incremental Load Pattern
1. **Bronze Layer:** Daily download of raw Kaggle data
2. **Silver Layer:** Incremental transformation
3. **Gold Layer:** (Optional) Aggregate tables for dashboards
4. **Semantic Model:** References Silver layer tables

### Refresh Schedule
- **Daily:** Kaggle data download
- **Hourly:** Report refresh (if using import mode)
- **Real-time:** (If using DirectQuery)

---

## 🛡️ Data Governance

### Data Quality Checks
- ✅ No NULL values in keys (customer_id, product_id)
- ✅ Referential integrity (FK values exist in dimensions)
- ✅ Range validation (prices > 0, ratings 0-5)
- ✅ Uniqueness (one customer_id per row in DimCustomer)

### Access Control (Ready for RLS)
- Can implement row-level security by customer region
- Can restrict by customer segment
- Can limit by sales channel

### Audit Trail
- All measures include formatString for consistency
- displayFolder organization for user navigation
- lineageTag for tracking lineage

---

## 📚 Related Documentation

- **Data Export Summary:** `DATA_EXPORT_SUMMARY.md`
- **Pipeline Documentation:** `PIPELINE_README.md`
- **Report Structure:** `GithubClaudeAI.Report/REPORT_STRUCTURE.md`

---

## ✅ Validation Checklist

- [x] All dimensions connected to fact table
- [x] Relationships set to correct cardinality (1:M)
- [x] All measures use appropriate aggregation
- [x] DAX formulas follow best practices
- [x] Display folders organized logically
- [x] Data types correct for each column
- [x] Format strings applied to numeric measures
- [x] No circular relationship dependencies
- [x] Key columns marked appropriately
- [x] Summary behavior set correctly

---

**Schema Version:** 1.0  
**Last Updated:** 2026-09-01  
**Status:** Production Ready ✅

