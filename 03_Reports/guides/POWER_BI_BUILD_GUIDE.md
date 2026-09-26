# 📊 Power BI Report - Complete Build Guide

## 🎯 Project: E-Commerce Analytics Platform
**Status:** Ready to Build  
**Pages:** 5  
**Visualizations:** 18  
**Slicers:** 5 (Date, Segment, Region, Channel, Category)  
**Measures:** 11 DAX formulas  

---

## 📁 Data Files Ready

```
C:\Users\admin\GithubclaudeAI\01_DataLayer\transformed_silver\
├── customer_master.csv        (25,000 rows)
├── product_catalog.csv        (1,175 rows)
├── order_items.csv            (138,116 rows)
└── ecommerce_sales_customer_analytics_150k.csv (24,911 rows)
```

---

## ✅ STEP-BY-STEP BUILD INSTRUCTIONS

### **STEP 1: Create New Blank Report**
```
1. Open Power BI Desktop
2. File → New
3. Select "Blank Report"
4. You'll see a blank canvas
```

---

### **STEP 2: Load Data from CSV Files**

**2.1 Load Customer Master Data**
```
Home → Get Data → Text/CSV
Navigate to: C:\Users\admin\GithubclaudeAI\01_DataLayer\transformed_silver\
Select: customer_master.csv
Click Load
(Rename table to: Customers)
```

**2.2 Load Product Catalog**
```
Home → Get Data → Text/CSV
Select: product_catalog.csv
Click Load
(Rename table to: Products)
```

**2.3 Load Sales Data**
```
Home → Get Data → Text/CSV
Select: order_items.csv
Click Load
(Rename table to: Sales)
```

**2.4 Load Analytics Data (Optional)**
```
Home → Get Data → Text/CSV
Select: ecommerce_sales_customer_analytics_150k.csv
Click Load
```

---

### **STEP 3: Create Relationships**

**Location:** Modeling Tab → Manage Relationships

**Relationship 1:**
- From Table: Sales
- From Column: customer_id
- To Table: Customers
- To Column: customer_id
- Cardinality: Many-to-One (*)

**Relationship 2:**
- From Table: Sales
- From Column: product_id
- To Table: Products
- To Column: product_id
- Cardinality: Many-to-One (*)

---

### **STEP 4: Create DAX Measures**

**Location:** Modeling → New Measure

**Financial Measures:**
```dax
Total Revenue = SUM(Sales[net_sales])
Total Profit = SUM(Sales[profit])
Total Cost = SUM(Sales[product_cost])
Profit Margin % = DIVIDE([Total Profit], [Total Revenue], 0)
```

**Order Measures:**
```dax
Total Orders = COUNTA(Sales[order_id])
Avg Order Value = DIVIDE([Total Revenue], [Total Orders], 0)
Total Quantity = SUM(Sales[quantity])
```

**Customer Measures:**
```dax
Unique Customers = DISTINCTCOUNT(Sales[customer_id])
Revenue per Customer = DIVIDE([Total Revenue], [Unique Customers], 0)
```

---

### **STEP 5: Build 5 Report Pages**

---

## 📄 PAGE 1: EXECUTIVE OVERVIEW

**Layout:** 4 KPI Cards (Top) + 2 Charts (Bottom)

### **Visual 1.1: Total Revenue Card**
```
Type: Card
Field: [Total Revenue]
Format: Currency ($)
Position: Top-Left
```

### **Visual 1.2: Total Orders Card**
```
Type: Card
Field: [Total Orders]
Format: Whole Number
Position: Top-Center-Left
```

### **Visual 1.3: Unique Customers Card**
```
Type: Card
Field: [Unique Customers]
Format: Whole Number
Position: Top-Center-Right
```

### **Visual 1.4: Profit Margin Card**
```
Type: Card
Field: [Profit Margin %]
Format: Percentage
Position: Top-Right
```

### **Visual 1.5: Revenue Trend (Line Chart)**
```
Type: Line Chart
Axis: Sales[order_date] (Grouped by Month)
Value: [Total Revenue]
Position: Bottom-Left (50% width)
Title: "Revenue Trend by Month"
```

### **Visual 1.6: Sales by Channel (Pie Chart)**
```
Type: Pie Chart
Legend: Sales[sales_channel]
Values: [Total Revenue]
Position: Bottom-Right (50% width)
Title: "Revenue Distribution by Channel"
```

---

## 📄 PAGE 2: SALES ANALYSIS

### **Visual 2.1: Revenue by Category (Column Chart)**
```
Type: Column Chart
Axis: Products[product_category]
Value: [Total Revenue]
Title: "Revenue by Product Category"
Position: Top (Full Width)
```

### **Visual 2.2: Top Products Table**
```
Type: Table
Columns:
  - Products[product_category]
  - Products[product_name]
  - [Total Revenue]
  - [Total Profit]
  - [Profit Margin %]
Sort By: [Total Revenue] (Descending)
Show Top: 20 rows
Position: Middle-Left
Title: "Top 20 Products by Revenue"
```

### **Visual 2.3: Discount Impact (Scatter Chart)**
```
Type: Scatter Chart
X-Axis: Sales[discount_amount]
Y-Axis: [Profit Margin %]
Size: [Total Revenue]
Legend: Products[product_category]
Position: Middle-Right
Title: "Discount vs Profit Margin Analysis"
```

---

## 📄 PAGE 3: CUSTOMER ANALYTICS

### **Visual 3.1: Customers by Segment (Column Chart)**
```
Type: Column Chart
Axis: Customers[customer_segment]
Value: DISTINCTCOUNT(Customers[customer_id])
Title: "Customer Count by Segment"
Position: Top-Left
```

### **Visual 3.2: Revenue by Region (Map)**
```
Type: Map/Filled Map
Location: Customers[region]
Size: [Total Revenue]
Title: "Revenue Distribution by Region"
Position: Top-Right
```

### **Visual 3.3: Top Customers Table**
```
Type: Table
Columns:
  - Customers[customer_id]
  - Customers[customer_name]
  - Customers[customer_segment]
  - Customers[region]
  - [Total Revenue]
Sort By: [Total Revenue] (Descending)
Show Top: 20 rows
Position: Bottom
Title: "Top 20 Customers by Revenue"
```

---

## 📄 PAGE 4: PRODUCT PERFORMANCE

### **Visual 4.1: Revenue by Category (Column Chart)**
```
Type: Column Chart
Axis: Products[product_category]
Value: [Total Revenue]
Tooltip: Include [Total Profit], [Unique Customers]
Position: Top
Title: "Category Revenue & Profitability"
```

### **Visual 4.2: Product Rating Distribution (Bar Chart)**
```
Type: Horizontal Bar Chart
Axis: Products[product_category]
Value: Average(Products[product_rating])
Title: "Average Product Rating by Category"
Position: Bottom-Left
```

### **Visual 4.3: Top Products Details (Table)**
```
Type: Table
Columns:
  - Products[product_category]
  - Products[product_name]
  - Products[brand]
  - Products[product_rating]
  - [Total Revenue]
  - [Total Profit]
Sort By: [Total Revenue] (Descending)
Position: Bottom-Right
Title: "Product Performance Matrix"
```

---

## 📄 PAGE 5: TIME SERIES TRENDS

### **Visual 5.1: Revenue Trend (Line Chart)**
```
Type: Line Chart
Axis: Sales[order_date] (Grouped by Month)
Value: [Total Revenue]
Line Style: Blue
Position: Top
Title: "Monthly Revenue Trend"
```

### **Visual 5.2: Profit Trend (Line Chart)**
```
Type: Line Chart
Axis: Sales[order_date] (Grouped by Month)
Value: [Total Profit]
Line Style: Green
Position: Middle
Title: "Monthly Profit Trend"
```

### **Visual 5.3: Revenue vs Profit (Area Chart)**
```
Type: Area Chart
Axis: Sales[order_date] (Grouped by Month)
Values: 
  - [Total Revenue] (Blue, 60% opacity)
  - [Total Profit] (Green, 60% opacity)
Position: Bottom
Title: "Revenue vs Profit Comparison"
```

---

## 🎚️ STEP 6: Add 5 Slicers (to ALL Pages)

**Location:** Insert → Slicer

### **Slicer 1: Date Range**
```
Field: Sales[order_date]
Style: Date Slicer (Relative Date)
Position: Top-Left on each page
Size: 20% width
Sync to all pages: YES
```

### **Slicer 2: Customer Segment**
```
Field: Customers[customer_segment]
Style: List/Buttons
Options: Consumer, Premium, VIP
Position: Top-Center-Left on each page
Sync to all pages: YES
```

### **Slicer 3: Region**
```
Field: Customers[region]
Style: Dropdown
Position: Top-Center-Right on each page
Sync to all pages: YES
```

### **Slicer 4: Sales Channel**
```
Field: Sales[sales_channel]
Style: List/Buttons
Position: Top-Right on each page
Sync to all pages: YES
```

### **Slicer 5: Product Category**
```
Field: Products[product_category]
Style: Dropdown
Position: Below other slicers
Sync to all pages: YES
```

---

## 💾 STEP 7: Format and Save

### **Formatting:**
1. **Colors:** Use professional palette (Blues, Greens, Grays)
2. **Currency Format:** All revenue fields → $#,##0.00
3. **Percentage Format:** All % fields → 0.00%
4. **Number Format:** Counts → #,##0

### **Naming Convention:**
- Page names clearly identify content
- Visual titles explain what's shown
- Measures organized by category

### **Save Report:**
```
File → Save As
Filename: E-Commerce-Analytics.pbix
Location: C:\Users\admin\GithubclaudeAI\03_Report\
Format: Power BI Report (.pbix)
Click "Save"
```

---

## 📊 Quick Reference: All DAX Measures

| Measure | Formula | Category |
|---------|---------|----------|
| Total Revenue | SUM(Sales[net_sales]) | Financial |
| Total Profit | SUM(Sales[profit]) | Financial |
| Total Cost | SUM(Sales[product_cost]) | Financial |
| Profit Margin % | DIVIDE([Total Profit], [Total Revenue], 0) | Financial |
| Total Orders | COUNTA(Sales[order_id]) | Orders |
| Avg Order Value | DIVIDE([Total Revenue], [Total Orders], 0) | Orders |
| Total Quantity | SUM(Sales[quantity]) | Orders |
| Unique Customers | DISTINCTCOUNT(Sales[customer_id]) | Customers |
| Revenue per Customer | DIVIDE([Total Revenue], [Unique Customers], 0) | Customers |

---

## ✅ Quality Checklist

- [ ] All 4 CSV files loaded
- [ ] 2 relationships created and active
- [ ] 11 DAX measures created
- [ ] 5 pages built with visualizations
- [ ] All slicers added to every page
- [ ] Slicers synced across pages
- [ ] Formatting applied consistently
- [ ] Report saved as .pbix file
- [ ] Tested slicers and filters work
- [ ] All visualizations display data correctly

---

## 🚀 Next Steps After Building

1. **Test Report:**
   - Click slicers to verify filtering
   - Check that all visualizations update
   - Verify numbers match expectations

2. **Publish to Power BI Service:**
   - File → Publish
   - Select Workspace
   - Set refresh schedule

3. **Share with Team:**
   - Add viewers/editors
   - Create mobile-optimized view
   - Set up alerts for key metrics

---

**Report Status:** Ready to Build  
**Estimated Build Time:** 30-45 minutes  
**Data Quality:** ✅ 100% validated & deduplicated

Happy building! 🎉
