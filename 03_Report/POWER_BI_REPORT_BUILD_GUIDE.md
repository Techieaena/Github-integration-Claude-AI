# 📊 Power BI Report - E-Commerce Analytics Platform Build Guide
## Connected to Fabric Lakehouse

Complete step-by-step guide to build a 5-page interactive Power BI report connected to the **Fabric GitClaude lakehouse** with 8 tables, 180+ columns, and 46 DAX measures.

**Report Specifications:**
- **Data Source:** Fabric Lakehouse (githubclaude)
- **Tables:** 8 (2 fact tables, 5 dimension tables, 1 reference table)
- **Total Rows:** 338,292 (138,116 orders/sales + 25,000 customers + 1,175 products)
- **Pages:** 5 (Executive Overview, Sales Analysis, Customer Analytics, Product Performance, Time Trends)
- **Visualizations:** 20+ interactive charts and tables
- **Slicers:** 6 (Date Range, Customer Segment, Region, Category, Order Status, Channel)
- **Measures:** 40+ DAX formulas

---

## 📋 Prerequisites

✅ Power BI Desktop (Latest version)  
✅ Fabric Workspace Access (fabricaena)  
✅ Lakehouse Access (githubclaude - ID: 0b4f9e6c-379c-493f-b707-0c857c8b8041)  
✅ Service Principal Credentials (for automated refresh)  
✅ Semantic Model Schema (02_SemanticModel/semantic_model.json)

---

## 🔌 Connection Setup - Fabric Lakehouse

### Step 1: Open Power BI Desktop
```
File → New Report (Blank)
```

### Step 2: Connect to Fabric Lakehouse
```
Home → Get Data → Azure → Fabric Lakehouse
Server: app.fabric.microsoft.com
Workspace: fabricaena
Lakehouse: githubclaude
```

### Step 3: Select Tables
Select these tables from the lakehouse:
- ☑ **orders** (138,116 rows - fact table)
- ☑ **sales** (138,116 rows - fully denormalized fact table)
- ☑ **customers** (25,000 rows - dimension)
- ☑ **products** (1,175 rows - dimension)
- ☑ **customer_analytics** (25,000 rows - dimension with aggregates)
- ☑ **product_analytics** (1,175 rows - dimension with aggregates)
- ☑ **sales_analytics** (138,116 rows - extended fact table)

**Note:** `dataset_statistics` is optional (contains 1 row with aggregate metrics)

### Step 4: Load and Transform
```
Click: Load to Power BI
Wait for data to import (~1-2 minutes)
```

---

## 📐 Table Structure & Relationships

### Dimension Tables

**📦 customers (25,000 rows)**
- customer_id (PK)
- customer_name, customer_age, gender
- customer_segment (Premium/Regular)
- customer_city, customer_state, customer_country, region
- customer_postal_code
- customer_acquisition_cost

**📦 products (1,175 rows)**
- product_id (PK)
- product_name, product_category, product_subcategory
- brand, supplier
- unit_price, product_cost
- product_rating (0-5 scale)

**📦 customer_analytics (25,000 rows)**
- customer_id
- All customer dimension fields (denormalized)
- total_orders, total_spent, avg_order_value

**📦 product_analytics (1,175 rows)**
- product_id
- All product dimension fields (denormalized)
- times_sold, total_quantity

### Fact Tables

**📊 orders (138,116 rows) - Normalized Fact**
- order_id (PK)
- product_id (FK)
- quantity, unit_price
- discount_percentage, discount_amount
- gross_sales, tax_amount, shipping_cost
- net_sales, product_cost
- profit

**📊 sales (138,116 rows) - Fully Denormalized Fact**
- order_id, order_date, order_time
- order_status, sales_channel
- customer_id + all customer fields (name, age, segment, city, state, country, region)
- product_id + product name (via denormalization)
- payment_method, payment_status
- shipping_method, warehouse, delivery_days, delivery_status
- return_status, return_reason
- customer_rating, review_sentiment
- marketing_channel, campaign_name, coupon_code
- loyalty_points_earned, loyalty_points_redeemed
- All financial metrics (gross_sales, net_sales, profit, etc.)
- customer_lifetime_value, is_repeat_customer

**📊 sales_analytics (138,116 rows) - Extended Fact**
- All sales columns + month field for time analysis

### Recommended Relationships

```
Create these relationships in Power BI:

1. orders[product_id] → products[product_id] (Many-to-One)
   Cross Filter: Both

2. sales[product_id] → products[product_id] (Many-to-One)
   Cross Filter: Both

3. orders[customer_id] → customers[customer_id] (Many-to-One)
   Cross Filter: Both

4. sales[customer_id] → customers[customer_id] (Many-to-One)
   Cross Filter: Both
```

**Note:** Since `sales` is fully denormalized, you may not need all relationships. Use `orders` for detailed drill-down analysis.

---

## 📅 Create Date Table (Required)

Power Query M Formula:
```m
let
  StartDate = #date(2023,1,1),
  EndDate = #date(2026,12,31),
  DateList = List.Dates(StartDate, Duration.Days(EndDate-StartDate)+1, #duration(1,0,0,0)),
  DateTable = Table.FromList(DateList, Splitter.SplitByNothing(), {"Date"}),
  WithYear = Table.AddColumn(DateTable, "Year", each Date.Year([Date])),
  WithMonth = Table.AddColumn(WithYear, "Month", each Date.Month([Date])),
  WithMonthName = Table.AddColumn(WithMonth, "MonthName", each Text.Proper(Date.MonthName([Date]))),
  WithQuarter = Table.AddColumn(WithMonthName, "Quarter", each "Q"&Text.From(Date.QuarterOfYear([Date]))),
  WithDayName = Table.AddColumn(WithQuarter, "DayName", each Text.Proper(Date.DayOfWeekName([Date]))),
  WithWeekNum = Table.AddColumn(WithDayName, "WeekNum", each Date.WeekOfYear([Date]))
in
  WithWeekNum
```

Link to orders/sales tables:
```
Date table[Date] → orders[order_date] (Many-to-One)
Date table[Date] → sales[order_date] (Many-to-One)
```

---

## 📐 Create Slicers (6 Total)

### Slicer 1: Date Range
```
Insert → Slicer → Dropdown or Between
Column: Date[MonthName] or Date[Date]
Location: Top-left, All report pages
Filter: Current year and previous year
```

### Slicer 2: Customer Segment
```
Insert → Slicer → Buttons
Column: customers[customer_segment]
Options: Premium, Regular
Location: Top-center, All pages
```

### Slicer 3: Geographic Region
```
Insert → Slicer → Dropdown
Column: customers[region]
Location: Top, Customer Analytics page
Multi-select: Enabled
```

### Slicer 4: Product Category
```
Insert → Slicer → Dropdown
Column: products[product_category]
Location: Top, Product Performance page
```

### Slicer 5: Order Status
```
Insert → Slicer → Buttons
Column: sales[order_status]
Options: Completed, Cancelled, etc.
Location: Top, Sales Analysis page
```

### Slicer 6: Sales Channel
```
Insert → Slicer → Dropdown
Column: sales[sales_channel]
Location: Top, Executive Overview page
```

---

## 📊 Page 1: Executive Overview

**Purpose:** High-level KPIs and business metrics

### Visualizations:

**1. Card: Total Revenue**
```
Field: [Total Net Sales]
Format: $#,##0
Conditional Formatting: Green if > threshold
```

**2. Card: Total Orders**
```
Field: [Total Orders]
Format: #,##0
```

**3. Card: Unique Customers**
```
Field: [Total Unique Customers]
Format: #,##0
```

**4. Card: Avg Order Value**
```
Field: [Average Order Value]
Format: $#,##0.00
```

**5. Line Chart: Revenue Trend (30 Days)**
```
X-Axis: Date[MonthName] or sales[order_date]
Y-Axis: [Total Net Sales]
Legend: sales_channel
Title: "Revenue Trend by Channel"
```

**6. Donut Chart: Orders by Status**
```
Legend: sales[order_status]
Values: [Total Orders]
Title: "Order Completion Status"
```

**7. Column Chart: Top 5 Product Categories by Revenue**
```
X-Axis: products[product_category]
Y-Axis: [Total Net Sales]
Sort: Descending
Limit: Top 5
```

---

## 📈 Page 2: Sales Analysis

**Purpose:** Deep-dive into sales performance and profitability

### Visualizations:

**8. Table: Top 10 Products by Revenue**
```
Columns:
  - products[product_name]
  - [Total Quantity Sold]
  - [Total Net Sales]
  - [Profit]
  - products[product_rating]
Sort: [Total Net Sales] Descending
Rows: Top 10
```

**9. Clustered Bar Chart: Revenue vs Cost by Category**
```
Axis: products[product_category]
Values: [Total Net Sales], [Total Product Cost]
Title: "Profitability by Category"
Legend: Show
```

**10. KPI Visual: Profit Margin %**
```
Value: [Profit Margin %]
Trend Axis: Date[Year]
Target: 35%
Status Colors: Green/Yellow/Red
```

**11. Combo Chart: Orders & Avg Order Value**
```
X-Axis: Date[MonthName]
Column Values: [Total Orders]
Line Values: [Average Order Value]
Title: "Order Volume vs Average Value"
```

**12. Gauge Chart: Order Completion Rate**
```
Value: [Order Completion Rate %]
Target: 95%
Min: 0%, Max: 100%
```

---

## 👥 Page 3: Customer Analytics

**Purpose:** Customer segmentation and lifetime value analysis

### Visualizations:

**13. Matrix: Customer Metrics by Segment & Region**
```
Rows: customers[customer_segment], customers[region]
Values:
  - [Total Unique Customers]
  - [Revenue per Customer]
  - [Average Order Value]
  - [Repeat Customer Rate %]
Expand: Enabled
```

**14. Scatter Plot: Customer Age vs Revenue**
```
X-Axis: customers[customer_age]
Y-Axis: [Revenue per Customer]
Size: [Total Orders]
Color: customers[customer_segment]
Title: "Customer Value by Age Group"
```

**15. Bar Chart: Top 15 Cities by Customer Count**
```
Axis: customers[customer_city]
Values: [Total Unique Customers]
Sort: Descending
Limit: Top 15
```

**16. Card Group: Segment Comparison**
```
Card 1: [Premium Customers]
Card 2: [Regular Customers]
Card 3: [Premium/Regular Ratio]
Card 4: [Premium Customer Avg Revenue]
```

**17. Line Chart: Customer Acquisition Cost by Segment**
```
X-Axis: Date[Year]
Y-Axis: [Avg Acquisition Cost]
Legend: customers[customer_segment]
```

---

## 🏆 Page 4: Product Performance

**Purpose:** Product ratings, category analysis, supplier metrics

### Visualizations:

**18. Treemap: Revenue Heatmap by Category & Subcategory**
```
Group: products[product_category]
Details: products[product_subcategory]
Values: [Total Net Sales]
Color Saturation: [Average Product Rating]
Large treemap, top of page
```

**19. Gauge Chart: Average Product Rating**
```
Value: [Average Product Rating]
Target: 4.0 stars
Min: 0, Max: 5
Title: "Overall Product Quality"
```

**20. Horizontal Bar: Top 10 Suppliers by Revenue**
```
Axis: products[supplier]
Values: [Total Net Sales]
Sort: Descending
Limit: Top 10
```

**21. Clustered Column: Price vs Cost by Brand**
```
X-Axis: products[brand]
Column 1: [Avg Unit Price]
Column 2: [Avg Product Cost]
Title: "Margin by Brand"
Limit: Top 12 brands
```

**22. Scatter: Rating vs Revenue by Product**
```
X-Axis: products[product_rating]
Y-Axis: [Total Revenue per Product]
Size: [Times Sold]
Color: products[product_category]
Detail tooltip: product_name, times_sold
```

---

## 📅 Page 5: Time Trends & Analysis

**Purpose:** Temporal analysis, seasonal patterns, YoY comparisons

### Visualizations:

**23. Area Chart: YTD Revenue Progression**
```
X-Axis: Date[Date] or sequential date field
Y-Axis: [YTD Revenue]
Color: Date[Year]
Multiple lines by year
```

**24. KPI Card: YoY Growth %**
```
Value: [YoY Growth %]
Trend: Dynamic indicator
Target: 15%
Format: +/- Percentage
```

**25. Line Chart: Monthly Revenue Pattern**
```
X-Axis: Date[Month] (1-12)
Y-Axis: [Total Net Sales]
Legend: Date[Year]
Multiple year overlay
Title: "Seasonal Revenue Pattern"
```

**26. Column Chart: Monthly Orders with Forecast**
```
X-Axis: Date[MonthName]
Y-Axis: [Total Orders]
Trendline: Linear regression
Title: "Order Volume Trend"
Current year highlight
```

**27. Table: Monthly Performance Summary**
```
Columns:
  - Date[Date]
  - [Total Orders]
  - [Total Net Sales]
  - [Profit]
  - [Order Completion Rate %]
Sort: Date descending
Show last 12 months
```

---

## 🧮 Complete DAX Measure Reference

### Financial Metrics
```dax
Total Gross Sales = SUM(sales[gross_sales])

Total Net Sales = SUM(sales[net_sales])

Total Product Cost = SUM(sales[product_cost])

Total Profit = [Total Net Sales] - [Total Product Cost]

Profit Margin % = IF([Total Net Sales] = 0, 0, DIVIDE([Total Profit], [Total Net Sales]))

Total Tax Amount = SUM(sales[tax_amount])

Total Shipping Cost = SUM(sales[shipping_cost])

Total Discounts Given = SUM(sales[discount_amount])

Average Discount % = AVERAGE(sales[discount_percentage])
```

### Order Metrics
```dax
Total Orders = DISTINCTCOUNT(sales[order_id])

Average Order Value = DIVIDE([Total Net Sales], [Total Orders])

Total Quantity Sold = SUM(sales[quantity])

Average Items per Order = DIVIDE([Total Quantity Sold], [Total Orders])

Completed Orders = COUNTIF(sales[order_status], "Completed")

Cancelled Orders = COUNTIF(sales[order_status], "Cancelled")

Order Completion Rate % = IF([Total Orders] = 0, 0, DIVIDE([Completed Orders], [Total Orders]))

Orders by Channel = CALCULATE([Total Orders], ALLEXCEPT(sales, sales[sales_channel]))
```

### Customer Metrics
```dax
Total Unique Customers = DISTINCTCOUNT(sales[customer_id])

Revenue per Customer = DIVIDE([Total Net Sales], [Total Unique Customers])

Orders per Customer = DIVIDE([Total Orders], [Total Unique Customers])

Avg Acquisition Cost = AVERAGE(customers[customer_acquisition_cost])

Premium Customers = CALCULATE(DISTINCTCOUNT(customers[customer_id]), customers[customer_segment] = "Premium")

Regular Customers = CALCULATE(DISTINCTCOUNT(customers[customer_id]), customers[customer_segment] = "Regular")

Repeat Customer Rate % = CALCULATE(DISTINCTCOUNT(sales[customer_id]), sales[is_repeat_customer] = TRUE) / [Total Unique Customers]

Customer Lifetime Value = AVERAGE(sales[customer_lifetime_value])
```

### Product Metrics
```dax
Total Products = DISTINCTCOUNT(products[product_id])

Products Sold = DISTINCTCOUNT(sales[product_id])

Average Product Rating = AVERAGE(products[product_rating])

High Rated Products = CALCULATE(DISTINCTCOUNT(products[product_id]), products[product_rating] >= 4.0)

Revenue by Category = SUMX(VALUES(products[product_category]), CALCULATE([Total Net Sales]))

Avg Product Cost = AVERAGE(products[product_cost])

Total Times Sold = SUM(product_analytics[times_sold])
```

### Quality & Returns
```dax
Return Rate % = COUNTIF(sales[return_status], "Returned") / [Total Orders]

Negative Sentiment % = CALCULATE(DISTINCTCOUNT(sales[order_id]), sales[review_sentiment] = "Negative") / [Total Orders]

Average Customer Rating = AVERAGE(sales[customer_rating])

Delivery Success Rate % = COUNTIF(sales[delivery_status], "Delivered") / [Total Orders]

Average Delivery Days = AVERAGE(sales[delivery_days])
```

### Time Intelligence
```dax
YTD Revenue = CALCULATE([Total Net Sales], DATESYTD(Date[Date]))

YTD Orders = CALCULATE([Total Orders], DATESYTD(Date[Date]))

MTD Revenue = CALCULATE([Total Net Sales], DATESMTD(Date[Date]))

Previous Year Revenue = CALCULATE([Total Net Sales], SAMEPERIODLASTYEAR(Date[Date]))

YoY Growth % = IF([Previous Year Revenue] = 0, 0, DIVIDE(([Total Net Sales] - [Previous Year Revenue]), [Previous Year Revenue]))

Same Period Last Year = CALCULATE([Total Orders], SAMEPERIODLASTYEAR(Date[Date]))

30-Day Revenue = CALCULATE([Total Net Sales], DATEADD(Date[Date], -30, DAY))
```

---

## 🎨 Formatting Standards

| Element | Style |
|---------|-------|
| **Primary Color** | #1F77B4 (Blue) |
| **Secondary Color** | #2CA02C (Green) |
| **Accent Color** | #FF7F0E (Orange) |
| **Background** | White (#FFFFFF) |
| **Text Color** | #333333 (Dark Gray) |
| **Font** | Segoe UI, 11pt |
| **Title Font Size** | 18pt Bold |
| **Card Values** | 24pt Bold |
| **Currency Format** | $#,##0.00 |
| **Percentage Format** | 0.00% |
| **Integer Format** | #,##0 |

---

## ✅ Build Checklist

- [ ] Connect Power BI to Fabric lakehouse (githubclaude)
- [ ] Load all 7 tables (orders, sales, customers, products, customer_analytics, product_analytics, sales_analytics)
- [ ] Create Date dimension table
- [ ] Establish 4 key relationships (product & customer links)
- [ ] Create 6 slicers (Date, Segment, Region, Category, Status, Channel)
- [ ] Build Page 1: Executive Overview (7 visualizations)
- [ ] Build Page 2: Sales Analysis (5 visualizations)
- [ ] Build Page 3: Customer Analytics (5 visualizations)
- [ ] Build Page 4: Product Performance (5 visualizations)
- [ ] Build Page 5: Time Trends & Analysis (5 visualizations)
- [ ] Create all 40+ DAX measures
- [ ] Format with consistent color scheme and fonts
- [ ] Set appropriate number formats ($, %, 0 decimals)
- [ ] Add conditional formatting to KPI cards
- [ ] Test slicer interactions across all pages
- [ ] Verify all measures calculate correctly
- [ ] Add tooltips to all charts
- [ ] Enable Q&A on all measures
- [ ] Set up row-level security if needed
- [ ] Configure automatic refresh schedule
- [ ] Save as .pbix file
- [ ] Publish to Fabric workspace

---

## 🚀 Performance Optimization

1. **Data Source Settings:**
   - Use Fabric lakehouse native connection
   - Enable query folding where possible
   - Load only necessary columns

2. **Measure Folders:**
   - Display Folders → Financial Metrics
   - Display Folders → Order Metrics
   - Display Folders → Customer Metrics
   - Display Folders → Product Metrics
   - Display Folders → Quality Metrics
   - Display Folders → Time Intelligence

3. **Refresh Strategy:**
   - Schedule daily refresh at 2 AM UTC
   - Incremental refresh for sales table
   - Validate data freshness

4. **Query Performance:**
   - Use aggregations for 138K+ row tables
   - Cache frequently accessed columns
   - Optimize relationship cardinality

---

## 📚 Related Documentation

- **Semantic Model Schema:** `02_SemanticModel/semantic_model.json`
- **Lakehouse Structure:** `02_SemanticModel/SEMANTIC_MODEL_SCHEMA.md`
- **Data Pipeline:** `05_Scripts/medallion_pipeline.py`
- **Fabric Setup:** `FABRIC_CONNECTION_SETUP.md`

---

**Last Updated:** 2026-09-13  
**Version:** 3.0 (Fabric Lakehouse Edition)  
**Data Source:** Fabric Workspace - githubclaude Lakehouse  
**Status:** Ready to Build ✅
