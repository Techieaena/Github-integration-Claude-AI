# 📊 Power BI Report - E-Commerce Analytics Platform Build Guide

## Overview
Complete step-by-step guide to build a 5-page interactive Power BI report connected to the new semantic model with star schema (32+ DAX measures, 3 relationships).

**Report Specifications:**
- **Pages:** 5 (Executive Overview, Sales Analysis, Customer Analytics, Product Performance, Time Trends)
- **Visualizations:** 18+ interactive charts and tables
- **Slicers:** 5 (Date Range, Customer Segment, Geographic Region, Product Category, Order Status)
- **Measures:** 32 DAX formulas across 6 categories
- **Data Source:** Semantic model in 02_SemanticModel/ (star schema: 5 tables, 138K fact rows)

---

## 📋 Prerequisites

✅ Power BI Desktop (Latest version)  
✅ Semantic Model Created (02_SemanticModel/ folder)  
✅ Data Layer Complete (01_DataLayer/transformed_silver/ with 4 CSV files)  
✅ TMDL Model Files Ready:
- `database.tmdl`, `model.tmdl`, `relationships.tmdl`
- `tables/DimCustomer.tmdl`, `DimProduct.tmdl`, `DimDate.tmdl`, `FactSales.tmdl`, `Measures.tmdl`
- `cultures/en-US.tmdl`

---

## 🔌 Connection Setup (Option A: Connect to Semantic Model)

### Step 1: Open Power BI Desktop
```
File → New Report (Blank)
```

### Step 2: Get Data from Semantic Model
```
Home → Get Data → Analysis Services or Power BI Datasets
Server/Dataset: [Your Fabric workspace path]
Database: E-Commerce Analytics
Select table:
  ☑ DimCustomer
  ☑ DimProduct
  ☑ DimDate
  ☑ FactSales
  ☑ Measures
Click Load
```

**Relationships Auto-Populate:**
- FactSales[customer_id] → DimCustomer[customer_id]
- FactSales[product_id] → DimProduct[product_id]
- FactSales[order_date] → DimDate[FullDate]

---

## 🔌 Connection Setup (Option B: Direct CSV Load)

### Step 1: Load Customer Data
```
Home → Get Data → Text/CSV
Browse: C:\Users\admin\GithubclaudeAI\01_DataLayer\transformed_silver\customer_master.csv
Load → Rename to: DimCustomer
```

### Step 2: Load Product Data
```
Home → Get Data → Text/CSV
Browse: product_catalog.csv
Load → Rename to: DimProduct
```

### Step 3: Load Date Dimension (Optional - Create in Power Query)
```
New Table (Power Query):
let
  StartDate = #date(2020,1,1),
  EndDate = #date(2025,12,31),
  DateList = List.Dates(StartDate, Duration.Days(EndDate-StartDate)+1, #duration(1,0,0,0)),
  DateTable = Table.FromList(DateList, Splitter.SplitByNothing(), {"FullDate"}),
  WithYear = Table.AddColumn(DateTable, "Year", each Date.Year([FullDate])),
  WithMonth = Table.AddColumn(WithYear, "Month", each Date.Month([FullDate])),
  WithMonthName = Table.AddColumn(WithMonth, "MonthName", each Text.Proper(Date.MonthName([FullDate]))),
  WithQuarter = Table.AddColumn(WithMonthName, "Quarter", each "Q"&Text.From(Date.QuarterOfYear([FullDate])))
in
  WithQuarter
```

### Step 4: Load Sales Data
```
Home → Get Data → Text/CSV
Browse: order_items.csv
Load → Rename to: FactSales
```

### Step 5: Create Relationships
```
Modeling → Manage Relationships

Relationship 1:
  From: FactSales[customer_id] → To: DimCustomer[customer_id]
  Cardinality: Many-to-One
  Cross Filter Direction: Both

Relationship 2:
  From: FactSales[product_id] → To: DimProduct[product_id]
  Cardinality: Many-to-One
  Cross Filter Direction: Both

Relationship 3:
  From: FactSales[order_date] → To: DimDate[FullDate]
  Cardinality: Many-to-One
  Cross Filter Direction: Both
```

---

## 📐 Create Slicers (5 Total)

### Slicer 1: Date Range
```
Insert → Slicer → Dropdown
Column: DimDate[MonthName]
Location: Top-left, Page: Executive Overview & Sales Analysis
Style: Blue theme
```

### Slicer 2: Customer Segment
```
Insert → Slicer → Buttons
Column: DimCustomer[customer_segment]
Options: Premium, Regular
Location: Top, Page: All pages
```

### Slicer 3: Geographic Region
```
Insert → Slicer → Dropdown
Column: DimCustomer[region]
Location: Top, Page: Customer Analytics
```

### Slicer 4: Product Category
```
Insert → Slicer → Dropdown
Column: DimProduct[product_category]
Location: Top, Page: Product Performance
```

### Slicer 5: Order Status
```
Insert → Slicer → Buttons
Column: FactSales[order_status]
Options: Completed, Cancelled
Location: Top, Page: Sales Analysis
```

---

## 📊 Page 1: Executive Overview

**Purpose:** High-level KPIs and business metrics at a glance

### Visualizations:

**1. Card: Total Revenue**
```
Field: Measures[Total Revenue]
Format: $#,##0.00
Size: Large (48pt font)
Location: Top-left
```

**2. Card: Gross Profit**
```
Field: Measures[Gross Profit]
Format: $#,##0.00
Location: Top-center
```

**3. Card: Total Orders**
```
Field: Measures[Total Orders]
Format: 0
Location: Top-right
```

**4. Card: Unique Customers**
```
Field: Measures[Total Unique Customers]
Format: 0
Location: Middle-left
```

**5. Line Chart: Revenue Trend**
```
X-Axis: DimDate[Month] (sorted by Month)
Y-Axis: Measures[Total Revenue]
Location: Middle (wide span)
Title: "30-Day Revenue Trend"
Tooltips: Month, Revenue, Orders
```

**6. Donut Chart: Sales by Segment**
```
Legend: DimCustomer[customer_segment]
Values: Measures[Total Revenue]
Location: Bottom-right
Title: "Revenue Distribution by Customer Segment"
```

---

## 📈 Page 2: Sales Analysis

**Purpose:** Deep-dive into sales performance, orders, and fulfillment

### Visualizations:

**7. Table: Top 10 Products by Revenue**
```
Columns: DimProduct[product_name], Measures[Total Sales], Measures[Total Orders], DimProduct[product_rating]
Sort: Measures[Total Sales] Descending
Rows: Top 10
Location: Left panel
```

**8. Clustered Bar Chart: Revenue vs Cost by Category**
```
Axis: DimProduct[product_category]
Values: Measures[Total Revenue], Measures[Total Cost]
Location: Center
Title: "Profitability by Category"
```

**9. KPI Visual: Profit Margin**
```
Value: Measures[Gross Profit Margin %]
Trend Axis: DimDate[Year]
Comparison: Measures[Previous Year Revenue]
Location: Top-right
Target: 35%
```

**10. Combo Chart: Orders & Avg Order Value by Month**
```
X-Axis: DimDate[MonthName]
Column Values: Measures[Total Orders]
Line Values: Measures[Average Order Value]
Location: Bottom
```

---

## 👥 Page 3: Customer Analytics

**Purpose:** Customer segmentation, acquisition cost, lifetime value

### Visualizations:

**11. Matrix: Customer Segmentation Analysis**
```
Rows: DimCustomer[customer_segment], DimCustomer[customer_city]
Values: 
  - Measures[Total Unique Customers]
  - Measures[Revenue per Customer]
  - Measures[Customer Acquisition Cost Avg]
Location: Left/Center
Expand/collapse enabled
```

**12. Scatter Plot: Age vs Revenue per Customer**
```
X-Axis: DimCustomer[customer_age]
Y-Axis: Measures[Revenue per Customer]
Size: Measures[Total Orders]
Color: DimCustomer[customer_segment]
Location: Right
```

**13. Bar Chart: Top 10 Cities by Customer Count**
```
Axis: DimCustomer[customer_city]
Values: Measures[Total Unique Customers]
Sort: Descending
Rows: Top 10
Location: Bottom-left
```

**14. KPI: Premium vs Regular Customers**
```
Card 1: Measures[Premium Customers]
Card 2: Measures[Regular Customers]
Location: Top
Comparison: Ratio display
```

---

## 🏆 Page 4: Product Performance

**Purpose:** Product ratings, category performance, supplier analysis

### Visualizations:

**15. Treemap: Revenue Heatmap by Category & Subcategory**
```
Group: DimProduct[product_category]
Details: DimProduct[product_subcategory]
Values: Measures[Total Revenue]
Color Saturation: Measures[Average Product Rating]
Location: Top (large)
```

**16. Gauge Chart: Average Product Rating**
```
Value: Measures[Average Product Rating]
Target: 4.5
Minimum: 0
Maximum: 5
Location: Top-right
```

**17. Horizontal Bar: Top Suppliers by Revenue**
```
Axis: DimProduct[supplier]
Values: Measures[Total Revenue]
Sort: Descending
Rows: Top 5
Location: Bottom-left
```

**18. Clustered Column: Unit Price vs Product Cost by Brand**
```
X-Axis: DimProduct[brand]
Column 1: DimProduct[unit_price]
Column 2: DimProduct[product_cost]
Location: Bottom-right
```

---

## 📅 Page 5: Time Trends & Intelligence

**Purpose:** Temporal analysis, YoY comparisons, seasonal patterns

### Visualizations:

**19. Area Chart: YTD Revenue Progression**
```
X-Axis: DimDate[DayOfYear]
Y-Axis: Measures[YTD Revenue]
Color: DimDate[Year]
Multiple lines by year
Location: Top
```

**20. KPI Card: YoY Growth %**
```
Value: Measures[YoY Growth %]
Trend Indicator: Dynamic
Target: 15%
Location: Top-left
Format: Percentage
```

**21. Line Chart: Monthly Revenue Pattern**
```
X-Axis: DimDate[Month]
Y-Axis: Measures[Total Revenue]
Legend: DimDate[Year]
Location: Center
Multiple year overlay
```

**22. Column Chart: Monthly Orders with Trendline**
```
X-Axis: DimDate[MonthName]
Y-Axis: Measures[Total Orders]
Trendline: Linear
Location: Bottom
```

---

## 🧮 Complete DAX Measure Reference

### Financial Metrics
```dax
Total Sales = SUMX(FactSales, FactSales[quantity] * FactSales[unit_price])
Total Revenue = SUMX(FactSales, (FactSales[quantity] * FactSales[unit_price]) * (1 - FactSales[discount_percent]) + FactSales[tax_amount] + FactSales[shipping_cost])
Total Cost = SUMX(FactSales, FactSales[quantity] * RELATED(DimProduct[product_cost]))
Gross Profit = [Total Revenue] - [Total Cost]
Gross Profit Margin % = IF([Total Revenue] = 0, 0, DIVIDE([Gross Profit], [Total Revenue]))
Total Discount Amount = SUMX(FactSales, (FactSales[quantity] * FactSales[unit_price]) * FactSales[discount_percent])
Total Tax Amount = SUM(FactSales[tax_amount])
Total Shipping Cost = SUM(FactSales[shipping_cost])
```

### Order Metrics
```dax
Total Orders = DISTINCTCOUNT(FactSales[order_id])
Average Order Value = DIVIDE([Total Revenue], [Total Orders])
Total Order Items = SUM(FactSales[quantity])
Average Items per Order = DIVIDE([Total Order Items], [Total Orders])
Completed Orders = COUNTIF(FactSales[order_status], "Completed")
Cancelled Orders = COUNTIF(FactSales[order_status], "Cancelled")
Order Completion Rate % = IF([Total Orders] = 0, 0, DIVIDE([Completed Orders], [Total Orders]))
```

### Customer Metrics
```dax
Total Unique Customers = DISTINCTCOUNT(FactSales[customer_id])
Revenue per Customer = DIVIDE([Total Revenue], [Total Unique Customers])
Orders per Customer = DIVIDE([Total Orders], [Total Unique Customers])
Customer Acquisition Cost Avg = AVERAGE(DimCustomer[customer_acquisition_cost])
Premium Customers = CALCULATE(DISTINCTCOUNT(DimCustomer[customer_id]), DimCustomer[customer_segment] = "Premium")
Regular Customers = CALCULATE(DISTINCTCOUNT(DimCustomer[customer_id]), DimCustomer[customer_segment] = "Regular")
```

### Product Metrics
```dax
Total Products = DISTINCTCOUNT(DimProduct[product_id])
Products Sold = DISTINCTCOUNT(FactSales[product_id])
Average Product Rating = AVERAGE(DimProduct[product_rating])
High Rated Products = CALCULATE(DISTINCTCOUNT(DimProduct[product_id]), DimProduct[product_rating] >= 4)
Revenue by Category = SUMX(VALUES(DimProduct[product_category]), CALCULATE([Total Revenue]))
```

### Quality Metrics
```dax
Quality Score = CALCULATE(AVERAGE(DimProduct[product_rating]))
Order Defect Rate % = IF([Total Orders] = 0, 0, DIVIDE([Cancelled Orders], [Total Orders]))
Average Discount % = AVERAGE(FactSales[discount_percent])
```

### Time Intelligence
```dax
YTD Revenue = CALCULATE([Total Revenue], DATESYTD(DimDate[FullDate]))
YTD Orders = CALCULATE([Total Orders], DATESYTD(DimDate[FullDate]))
MTD Revenue = CALCULATE([Total Revenue], DATESMTD(DimDate[FullDate]))
Previous Year Revenue = CALCULATE([Total Revenue], SAMEPERIODLASTYEAR(DimDate[FullDate]))
YoY Growth % = IF([Previous Year Revenue] = 0, 0, DIVIDE(([Total Revenue] - [Previous Year Revenue]), [Previous Year Revenue]))
Revenue Trend = CALCULATE([Total Revenue], DATEADD(DimDate[FullDate], -30, DAY))
```

---

## 🎨 Formatting Standards

| Element | Style |
|---------|-------|
| **Primary Color** | #2F5496 (Dark Blue) |
| **Secondary Color** | #70AD47 (Green) |
| **Accent Color** | #FFC000 (Gold) |
| **Background** | White (#FFFFFF) |
| **Text Color** | #333333 (Dark Gray) |
| **Font** | Segoe UI, 11pt |
| **Title Font Size** | 18pt Bold |
| **Card Values** | 24pt Bold |

---

## ✅ Build Checklist

- [ ] Create blank Power BI report
- [ ] Connect to semantic model or load CSV data
- [ ] Create 3 table relationships
- [ ] Add 5 slicers (Date, Segment, Region, Category, Status)
- [ ] Build Page 1: Executive Overview (6 visualizations)
- [ ] Build Page 2: Sales Analysis (4 visualizations)
- [ ] Build Page 3: Customer Analytics (4 visualizations)
- [ ] Build Page 4: Product Performance (4 visualizations)
- [ ] Build Page 5: Time Trends (4 visualizations)
- [ ] Format with consistent color scheme and fonts
- [ ] Add page-level filters where applicable
- [ ] Test slicer interactions across all pages
- [ ] Verify all measures calculate correctly
- [ ] Enable Q&A on all measures
- [ ] Set appropriate number formats ($, %, 0 decimals)
- [ ] Add bookmarks for drill-through navigation (optional)
- [ ] Save as .pbix file
- [ ] Publish to Power BI Service/Fabric workspace

---

## 🚀 Performance Optimization

1. **Measure Groups:** Organize measures in display folders
   ```
   Display Folders:
   - Financial Metrics
   - Order Metrics
   - Customer Metrics
   - Product Metrics
   - Quality Metrics
   - Time Intelligence
   ```

2. **Aggregation Tables:** For 100M+ row scenarios, create:
   - Daily aggregations by Category
   - Customer segment summaries
   - Product performance caches

3. **Refresh Schedule:** Fabric semantic model
   - Daily refresh at 2 AM UTC
   - Incremental refresh for FactSales table

4. **Query Folding:** Ensure Power Query folds filters to source

---

## 📚 Related Documentation

- **Semantic Model:** `02_SemanticModel/SCHEMA_DOCUMENTATION.md`
- **Data Layer:** `01_DataLayer/README.md`
- **Build Guide:** `05_Scripts/POWER_BI_BUILD_GUIDE.md`
- **Implementation:** `04_Documentation/Guides/POWER_BI_IMPLEMENTATION_GUIDE.md`

---

**Last Updated:** 2026-09-12  
**Version:** 2.0 (Updated with new semantic model)  
**Status:** Ready to Build
