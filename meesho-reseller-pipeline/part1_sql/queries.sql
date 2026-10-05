-- Part 1 - SQL Business Query Engine
-- Database: data/meesho_reseller.db   (run: sqlite3 data/meesho_reseller.db < part1_sql/queries.sql)
-- Tables : orders(order_id, reseller_id, month, category, quantity, unit_price, status)
--          resellers(reseller_id, reseller_name, region, city)
-- NOTE   : adjust column names below if the supplied generate_dataset.py names them differently.

-- Q1. Monthly revenue by category  -> part1_sql/output/monthly_category_revenue.csv
--     Columns EXACTLY: month, category, revenue, n_orders  (15 rows = 3 months x 5 categories)
--     SUM raw quantity * unit_price first, then ROUND ONCE (never round per row).
SELECT month,
       category,
       ROUND(SUM(quantity * unit_price), 2) AS revenue,
       COUNT(*)                             AS n_orders
FROM orders
GROUP BY month, category
ORDER BY CASE month WHEN 'April' THEN 1 WHEN 'May' THEN 2 WHEN 'June' THEN 3 END,
         category;

-- Q2. Region-wise total revenue and order count
--     Region totals must sum to the grand total 1262066.92 / 900 orders.
SELECT r.region,
       ROUND(SUM(o.quantity * o.unit_price), 2) AS total_revenue,
       COUNT(*)                                 AS order_count
FROM orders o
JOIN resellers r ON r.reseller_id = o.reseller_id
GROUP BY r.region
ORDER BY total_revenue DESC;

-- Q3. Top 5 resellers by total spend (> 50000)
--     HAVING (not WHERE): the aggregate does not exist until GROUP BY has run.
SELECT o.reseller_id,
       r.reseller_name,
       ROUND(SUM(o.quantity * o.unit_price), 2) AS total_spend
FROM orders o
JOIN resellers r ON r.reseller_id = o.reseller_id
GROUP BY o.reseller_id, r.reseller_name
HAVING total_spend > 50000
ORDER BY total_spend DESC
LIMIT 5;

-- Q4. Resellers who have never placed an order (exactly one: RS024)
--     LEFT JOIN keeps unmatched resellers, and order_id IS NULL isolates them.
SELECT r.reseller_id, r.reseller_name, r.region
FROM resellers r
LEFT JOIN orders o ON o.reseller_id = r.reseller_id
WHERE o.order_id IS NULL;

-- Q4b. REQUIRED concept: COUNT(*) vs COUNT(order_id) for RS024, side by side.
--      COUNT(*)        = 1  (counts the row itself - the LEFT JOIN row still exists, full of NULLs)
--      COUNT(order_id) = 0  (counts only non-NULL order_ids - the correct "zero orders" answer)
SELECT r.reseller_id,
       COUNT(*)          AS count_star,
       COUNT(o.order_id) AS count_order_id
FROM resellers r
LEFT JOIN orders o ON o.reseller_id = r.reseller_id
WHERE r.reseller_id = 'RS024'
GROUP BY r.reseller_id;

-- Q5. June Average Order Value, Delivered orders only (BOTH filters together)
--     Expected: 1267.69
SELECT ROUND(SUM(quantity * unit_price) / COUNT(*), 2) AS june_delivered_aov
FROM orders
WHERE month = 'June'
  AND status = 'Delivered';
