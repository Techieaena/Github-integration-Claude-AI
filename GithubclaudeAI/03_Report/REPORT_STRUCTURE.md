# 📊 Power BI Report Structure

## Star Schema Architecture

### Dimension Tables
1. **DimCustomer** - Customer demographics and attributes
   - PK: customer_id
   - Attributes: name, age, gender, segment, location, region, postal code, acquisition cost

2. **DimProduct** - Product catalog and details
   - PK: product_id
   - Attributes: name, category, subcategory, brand, supplier, unit price, cost, rating

3. **DimDate** - Date dimension for time intelligence
   - PK: DateKey
   - Attributes: Year, Month, Quarter, Day, Week, Day Name, etc.

### Fact Table
1. **FactSales** - Main transaction facts
   - FK: customer_id → DimCustomer
   - FK: order_date → DimDate
   - Measures: quantity, gross_sales, discount, tax, shipping, net_sales, cost, profit
   - Attributes: order_id, order_status, payment_method, shipping_method, etc.

### Relationships
- FactSales → DimCustomer (Many-to-One)
- FactSales → DimDate (Many-to-One)
- Both relationships set to bidirectional filtering

---

## DAX Measures Created

### Financial Metrics
- **Total_Revenue** - Sum of net sales
- **Total_Gross_Sales** - Sum of gross sales
- **Total_Profit** - Sum of profit
- **Total_Discount** - Sum of discounts
- **Total_Tax** - Sum of taxes
- **Total_Shipping** - Sum of shipping costs
- **Total_Cost** - Sum of product costs
- **Profit_Margin_Percent** - Profit as % of revenue

### Order Metrics
- **Total_Orders** - Count of unique orders
- **Total_Items_Sold** - Sum of quantities
- **Average_Order_Value** - Revenue per order
- **Average_Items_Per_Order** - Items per order
- **Completed_Orders** - Orders with "Completed" status
- **Order_Completion_Rate** - % of completed orders

### Customer Metrics
- **Unique_Customers** - Distinct customer count
- **Repeat_Purchase_Count** - Customers with repeat purchases
- **Repeat_Customer_Rate** - % of repeat customers
- **Average_Customer_Rating** - Average rating
- **Revenue_per_Customer** - Revenue divided by customer count
- **Profit_per_Customer** - Profit divided by customer count

### Delivery & Quality Metrics
- **On_Time_Delivery_Count** - Orders delivered on time
- **On_Time_Delivery_Rate** - % on-time delivery
- **Return_Rate** - % of orders with returns
- **Average_Customer_Rating** - Customer satisfaction

### Time Intelligence Measures
- **Revenue_YoY_Growth** - Year-over-Year growth %
- **Revenue_MoM_Growth** - Month-over-Month growth %
- **Revenue_YTD** - Year-to-Date revenue
- **Profit_YTD** - Year-to-Date profit
- **Orders_YTD** - Year-to-Date orders

---

## Report Pages

### Page 1: Executive Overview
**Purpose:** High-level KPIs and business health snapshot

**Visualizations:**
1. **KPI Cards** (Top Row)
   - Total Revenue (YTD)
   - Total Orders (YTD)
   - Unique Customers
   - Average Order Value

2. **KPI Cards** (Second Row)
   - Total Profit (YTD)
   - Profit Margin %
   - Order Completion Rate
   - On-Time Delivery Rate

3. **Revenue Trend** (Line Chart)
   - Revenue by Month
   - Profit overlay
   - Trend line

4. **Order Status Distribution** (Pie Chart)
   - Completed vs Cancelled vs Pending

5. **Sales Channel Performance** (Column Chart)
   - Revenue by sales channel
   - Order count overlay

### Page 2: Sales Analysis
**Purpose:** Deep dive into revenue and profitability

**Visualizations:**
1. **Revenue Overview** (Multi-Row Card)
   - Total Revenue
   - Gross Sales
   - Discounts Given
   - Net Sales

2. **Profitability Metrics** (Multi-Row Card)
   - Total Profit
   - Total Cost
   - Profit Margin %
   - Revenue per Order

3. **Revenue by Category** (Column Chart)
   - Revenue by product category
   - Profit overlay

4. **Top 10 Products** (Table)
   - Product name, category
   - Revenue, Profit, Margin %
   - Order count

5. **Sales by Payment Method** (Donut Chart)
   - Revenue split by payment method

6. **Discount Impact** (Scatter Chart)
   - Discount % vs Profit Margin
   - By product category

### Page 3: Customer Analytics
**Purpose:** Customer behavior and segmentation

**Visualizations:**
1. **Customer Overview** (Multi-Row Card)
   - Unique Customers
   - Repeat Customer Rate
   - Revenue per Customer
   - Avg Rating

2. **Customer by Segment** (Column Chart)
   - Customer count by segment
   - Revenue by segment

3. **Customer by Region** (Map/Table)
   - Customers by country/region
   - Revenue by location

4. **Customer Lifetime Value** (Table)
   - Top 20 customers
   - Total spend, Orders, Avg order value

5. **Repeat Purchase Analysis** (Line Chart)
   - Repeat customer % over time
   - Trend by segment

6. **Customer Rating Distribution** (Histogram)
   - Distribution of ratings
   - Sentiment breakdown

### Page 4: Product Performance
**Purpose:** Product-level metrics and optimization

**Visualizations:**
1. **Product Overview** (Multi-Row Card)
   - Total Products
   - Avg Rating
   - Top Category
   - Avg Price

2. **Product Rating by Category** (Column Chart)
   - Average rating by category
   - Sample size

3. **Top Performers** (Table)
   - Top products by revenue
   - Top products by profit
   - Top products by order count

4. **Category Profitability** (Column Chart)
   - Revenue, Cost, Profit by category
   - Margin % line

5. **Product Price vs Sales** (Scatter Chart)
   - Unit price vs order quantity
   - By category

6. **Category Mix** (Pie Chart)
   - Revenue percentage by category

### Page 5: Time Series & Trends
**Purpose:** Temporal analysis and forecasting context

**Visualizations:**
1. **YTD Performance** (Multi-Row Card)
   - Revenue YTD
   - Profit YTD
   - Orders YTD
   - Avg Order Value YTD

2. **Revenue Trend** (Line Chart)
   - Daily revenue
   - 7-day moving average
   - Previous year comparison

3. **Growth Rates** (Combo Chart)
   - Revenue line chart
   - YoY Growth % bars
   - MoM Growth % secondary axis

4. **Seasonal Analysis** (Heatmap)
   - Revenue by month and category
   - Color intensity = revenue

5. **Delivery Performance Trend** (Line Chart)
   - On-time delivery % over time
   - Return rate over time

6. **Sales Channel Trends** (Area Chart)
   - Revenue by channel over time
   - Stacked by channel

---

## Interactivity Features

### Slicers (Available on All Pages)
1. **Date Range** - Start and end date picker
2. **Customer Segment** - Consumer, Premium, VIP
3. **Region** - Geography filter
4. **Sales Channel** - Mobile App, Website, In-Store
5. **Product Category** - Electronics, Apparel, etc.

### Drill-Through Actions
- Click on product → Product detail page
- Click on customer → Customer detail page
- Click on date → Daily sales detail

### Tooltips
- Enhanced tooltips showing:
  - Actual values
  - % of total
  - Prior period comparison
  - Target vs Actual (if applicable)

---

## Color Scheme & Formatting

### Color Palette
- **Revenue/Positive:** Green (#107C10)
- **Profit/Performance:** Blue (#0078D4)
- **Costs/Negative:** Red (#D83B01)
- **Neutral:** Gray (#605E5C)

### Number Formats
- Currency: $#,##0.00
- Percentage: 0.00%
- Whole Numbers: #,##0
- Decimals: 0.00

---

## Performance Optimizations

1. **Data Model**
   - Star schema minimizes redundancy
   - Efficient relationships for filtering
   - Aggregate tables for large fact tables

2. **DAX**
   - Use CALCULATE for complex filtering
   - Avoid circular dependencies
   - Efficient use of FILTER and SUMX

3. **Report**
   - Separate high-level KPI page
   - Drill-through instead of nested filters
   - Appropriate use of aggregations

---

## Next Steps

1. Connect to actual data sources (transformed_silver tables)
2. Validate all DAX measures against source data
3. Create additional drill-through pages for details
4. Set up automatic refresh schedule
5. Configure row-level security (RLS) if needed
6. Publish to Power BI Service

