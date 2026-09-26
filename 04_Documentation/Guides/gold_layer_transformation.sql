-- ============================================================================
-- GOLD LAYER TRANSFORMATION - SQL ANALYTICAL ENDPOINT
-- ============================================================================
-- Purpose: Create dimensional and fact tables for business analytics
-- Location: Fabric SQL Analytical Endpoint
-- Input: Silver layer Delta tables
-- Output: Gold layer analytical tables in Delta format
-- ============================================================================

-- ============================================================================
-- 1. DIMENSIONAL TABLES
-- ============================================================================

-- Customer Dimension Table
CREATE OR REPLACE TABLE gold.dim_customer AS
SELECT
    CustomerID,
    CustomerName,
    Email,
    Phone,
    Address,
    City,
    State,
    Country,
    ZipCode,
    processed_date as load_date,
    CURRENT_TIMESTAMP() as created_at
FROM silver.customer_silver;

-- Product Dimension Table
CREATE OR REPLACE TABLE gold.dim_product AS
SELECT
    ProductID,
    ProductName,
    Category,
    SubCategory,
    Price,
    processed_date as load_date,
    CURRENT_TIMESTAMP() as created_at
FROM silver.products_silver;

-- Date Dimension (for time-based analytics)
CREATE OR REPLACE TABLE gold.dim_date AS
WITH date_range AS (
    SELECT DISTINCT CAST(OrderDate AS DATE) as date_value
    FROM silver.sales_silver
    WHERE OrderDate IS NOT NULL
)
SELECT
    CAST(date_value AS DATE) as date_key,
    EXTRACT(YEAR FROM date_value) as year,
    EXTRACT(MONTH FROM date_value) as month,
    EXTRACT(QUARTER FROM date_value) as quarter,
    EXTRACT(DAY FROM date_value) as day_of_month,
    EXTRACT(WEEK FROM date_value) as week_of_year,
    DAYNAME(date_value) as day_name,
    MONTHNAME(date_value) as month_name,
    CASE
        WHEN EXTRACT(MONTH FROM date_value) >= 1 AND EXTRACT(MONTH FROM date_value) <= 3 THEN 'Q1'
        WHEN EXTRACT(MONTH FROM date_value) >= 4 AND EXTRACT(MONTH FROM date_value) <= 6 THEN 'Q2'
        WHEN EXTRACT(MONTH FROM date_value) >= 7 AND EXTRACT(MONTH FROM date_value) <= 9 THEN 'Q3'
        ELSE 'Q4'
    END as quarter_name
FROM date_range
ORDER BY date_key;

-- ============================================================================
-- 2. FACT TABLES
-- ============================================================================

-- Sales Fact Table
CREATE OR REPLACE TABLE gold.fact_sales AS
SELECT
    s.OrderID,
    s.CustomerID,
    CAST(s.OrderDate AS DATE) as order_date,
    s.Amount,
    s.Quantity,
    COUNT(DISTINCT oi.ProductID) as product_count,
    s.processed_date as load_date,
    CURRENT_TIMESTAMP() as created_at
FROM silver.sales_silver s
LEFT JOIN silver.order_items_silver oi ON s.OrderID = oi.OrderID
GROUP BY s.OrderID, s.CustomerID, CAST(s.OrderDate AS DATE), s.Amount, s.Quantity, s.processed_date;

-- Order Items Fact Table
CREATE OR REPLACE TABLE gold.fact_order_items AS
SELECT
    oi.OrderID,
    oi.ProductID,
    oi.Quantity,
    oi.UnitPrice,
    (oi.Quantity * oi.UnitPrice) as line_amount,
    oi.processed_date as load_date,
    CURRENT_TIMESTAMP() as created_at
FROM silver.order_items_silver oi;

-- ============================================================================
-- 3. ANALYTICAL VIEWS - CUSTOMER ANALYTICS
-- ============================================================================

-- Customer Segmentation (RFM Analysis)
CREATE OR REPLACE TABLE gold.customer_segmentation AS
SELECT
    c.CustomerID,
    c.CustomerName,
    c.Email,
    COUNT(DISTINCT s.OrderID) as total_orders,
    COUNT(DISTINCT DATE_TRUNC(MONTH, s.order_date)) as months_active,
    SUM(s.Amount) as total_spending,
    AVG(s.Amount) as avg_order_value,
    MIN(s.Amount) as min_order_value,
    MAX(s.Amount) as max_order_value,
    MAX(s.order_date) as last_order_date,
    MIN(s.order_date) as first_order_date,
    DATEDIFF(day, MIN(s.order_date), MAX(s.order_date)) as customer_lifetime_days,
    DATEDIFF(day, MAX(s.order_date), CURRENT_DATE()) as days_since_last_order,
    CASE
        WHEN COUNT(DISTINCT s.OrderID) >= 10 AND SUM(s.Amount) > 5000 THEN 'VIP'
        WHEN COUNT(DISTINCT s.OrderID) >= 5 AND SUM(s.Amount) > 2000 THEN 'Regular'
        WHEN COUNT(DISTINCT s.OrderID) >= 2 AND SUM(s.Amount) > 500 THEN 'Active'
        ELSE 'Occasional'
    END as customer_segment,
    CASE
        WHEN DATEDIFF(day, MAX(s.order_date), CURRENT_DATE()) <= 30 THEN 'Recently Active'
        WHEN DATEDIFF(day, MAX(s.order_date), CURRENT_DATE()) <= 90 THEN 'Active'
        WHEN DATEDIFF(day, MAX(s.order_date), CURRENT_DATE()) <= 180 THEN 'At Risk'
        ELSE 'Inactive'
    END as customer_status,
    CURRENT_TIMESTAMP() as created_at
FROM gold.dim_customer c
LEFT JOIN gold.fact_sales s ON c.CustomerID = s.CustomerID
GROUP BY c.CustomerID, c.CustomerName, c.Email;

-- ============================================================================
-- 4. ANALYTICAL VIEWS - SALES ANALYTICS
-- ============================================================================

-- Sales by Category
CREATE OR REPLACE TABLE gold.sales_by_category AS
SELECT
    p.Category,
    p.SubCategory,
    COUNT(DISTINCT oi.OrderID) as total_orders,
    COUNT(DISTINCT s.CustomerID) as unique_customers,
    SUM(oi.line_amount) as total_sales_amount,
    AVG(oi.line_amount) as avg_order_line_value,
    SUM(oi.Quantity) as total_quantity_sold,
    COUNT(DISTINCT p.ProductID) as product_count,
    CURRENT_TIMESTAMP() as created_at
FROM gold.dim_product p
LEFT JOIN gold.fact_order_items oi ON p.ProductID = oi.ProductID
LEFT JOIN gold.fact_sales s ON oi.OrderID = s.OrderID
GROUP BY p.Category, p.SubCategory;

-- Monthly Sales Trends
CREATE OR REPLACE TABLE gold.monthly_sales_trend AS
SELECT
    DATE_TRUNC(MONTH, s.order_date) as sales_month,
    EXTRACT(YEAR FROM s.order_date) as year,
    EXTRACT(MONTH FROM s.order_date) as month,
    COUNT(DISTINCT s.OrderID) as order_count,
    COUNT(DISTINCT s.CustomerID) as unique_customers,
    SUM(s.Amount) as total_sales_amount,
    AVG(s.Amount) as avg_order_value,
    MIN(s.Amount) as min_order_value,
    MAX(s.Amount) as max_order_value,
    SUM(s.Quantity) as total_quantity_sold,
    CURRENT_TIMESTAMP() as created_at
FROM gold.fact_sales s
WHERE s.order_date IS NOT NULL
GROUP BY DATE_TRUNC(MONTH, s.order_date), EXTRACT(YEAR FROM s.order_date), EXTRACT(MONTH FROM s.order_date)
ORDER BY sales_month DESC;

-- Top Products
CREATE OR REPLACE TABLE gold.top_products AS
SELECT
    p.ProductID,
    p.ProductName,
    p.Category,
    p.SubCategory,
    p.Price,
    COUNT(DISTINCT oi.OrderID) as times_ordered,
    SUM(oi.Quantity) as total_quantity_sold,
    SUM(oi.line_amount) as total_revenue,
    AVG(oi.line_amount) as avg_order_line_value,
    AVG(oi.Quantity) as avg_quantity_per_order,
    RANK() OVER (ORDER BY SUM(oi.line_amount) DESC) as revenue_rank,
    RANK() OVER (ORDER BY COUNT(DISTINCT oi.OrderID) DESC) as popularity_rank,
    CURRENT_TIMESTAMP() as created_at
FROM gold.dim_product p
LEFT JOIN gold.fact_order_items oi ON p.ProductID = oi.ProductID
GROUP BY p.ProductID, p.ProductName, p.Category, p.SubCategory, p.Price
ORDER BY total_revenue DESC;

-- ============================================================================
-- 5. KEY METRICS & KPI TABLES
-- ============================================================================

-- Daily Sales Summary
CREATE OR REPLACE TABLE gold.daily_sales_summary AS
SELECT
    s.order_date,
    COUNT(DISTINCT s.OrderID) as orders_count,
    COUNT(DISTINCT s.CustomerID) as unique_customers,
    SUM(s.Amount) as daily_revenue,
    AVG(s.Amount) as avg_order_value,
    MIN(s.Amount) as min_order_value,
    MAX(s.Amount) as max_order_value,
    SUM(s.Quantity) as total_items_sold,
    CURRENT_TIMESTAMP() as created_at
FROM gold.fact_sales s
WHERE s.order_date IS NOT NULL
GROUP BY s.order_date
ORDER BY s.order_date DESC;

-- Customer Lifetime Value Analysis
CREATE OR REPLACE TABLE gold.customer_lifetime_value AS
SELECT
    cs.CustomerID,
    cs.CustomerName,
    cs.total_orders,
    cs.total_spending as lifetime_value,
    cs.customer_segment,
    cs.customer_status,
    CASE
        WHEN cs.total_spending >= 10000 THEN 'Very High Value'
        WHEN cs.total_spending >= 5000 THEN 'High Value'
        WHEN cs.total_spending >= 2000 THEN 'Medium Value'
        WHEN cs.total_spending >= 500 THEN 'Low Value'
        ELSE 'Minimal Value'
    END as clv_category,
    RANK() OVER (ORDER BY cs.total_spending DESC) as clv_rank,
    CURRENT_TIMESTAMP() as created_at
FROM gold.customer_segmentation cs
ORDER BY cs.total_spending DESC;

-- ============================================================================
-- 6. DATA QUALITY CHECKS
-- ============================================================================

-- Data Quality Report
CREATE OR REPLACE TABLE gold.data_quality_report AS
SELECT
    'customer_silver' as source_table,
    COUNT(*) as row_count,
    COUNT(DISTINCT CustomerID) as distinct_ids,
    COUNT(CASE WHEN CustomerID IS NULL THEN 1 END) as null_count,
    CURRENT_TIMESTAMP() as check_timestamp
FROM silver.customer_silver
UNION ALL
SELECT
    'sales_silver',
    COUNT(*),
    COUNT(DISTINCT OrderID),
    COUNT(CASE WHEN OrderID IS NULL THEN 1 END),
    CURRENT_TIMESTAMP()
FROM silver.sales_silver
UNION ALL
SELECT
    'order_items_silver',
    COUNT(*),
    COUNT(DISTINCT OrderID),
    COUNT(CASE WHEN OrderID IS NULL THEN 1 END),
    CURRENT_TIMESTAMP()
FROM silver.order_items_silver
UNION ALL
SELECT
    'products_silver',
    COUNT(*),
    COUNT(DISTINCT ProductID),
    COUNT(CASE WHEN ProductID IS NULL THEN 1 END),
    CURRENT_TIMESTAMP()
FROM silver.products_silver;

-- ============================================================================
-- 7. VALIDATION SUMMARY
-- ============================================================================

SELECT
    'Gold Layer Transformation Complete' as status,
    CURRENT_TIMESTAMP() as completion_time,
    'All dimensional, fact, and analytical tables created successfully' as message;
