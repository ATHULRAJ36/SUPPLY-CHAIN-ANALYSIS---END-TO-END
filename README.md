# 🚚 Supply Chain Analytics — End to End Project

> **Complete analytics pipeline:** Raw Excel data → Data Cleaning → MySQL Database → SQL Analysis → Power BI Dashboard

![Power BI Data Model](images/dashboard/powerbi_model.png)

---

## 📌 Project Overview

A full end-to-end supply chain analytics project built on a real-world dataset of **11,340 orders** across **5 suppliers**, **3 product types**, **4 transportation modes** and **5 warehouse locations** across India.

The project covers every stage of the analytics pipeline — from a messy, misnamed raw Excel file to a 5-page interactive Power BI dashboard with 80+ DAX measures.

---

## 🛠️ Tools and Technologies

| Tool | Purpose |
|---|---|
| Microsoft Excel | Data exploration and schema design |
| Python | Data cleaning and ETL automation |
| MySQL | Relational database and SQL analysis |
| Power BI Desktop | Interactive dashboard development |
| DAX | Business intelligence measures |

---

## 📁 Repository Structure

```
supply-chain-analytics-end-to-end/
│
├── README.md
│
├── data/
│   ├── raw/
│   │   └── SUPPLY_CHAIN_ANALYSIS.xlsx        ← original raw file (11,340 rows, 24 columns)
│   └── cleaned/
│       └── SUPPLY_CHAIN_DB_SCHEMA.xlsx        ← normalized star schema (7 sheets)
│
├── sql/
│   ├── 01_create_tables.sql                   ← CREATE TABLE with PKs and FKs
│   ├── 02_analysis_queries.sql                ← 14 analysis queries (beginner to advanced)
│   └── 03_supplier_scorecard.sql              ← capstone scorecard query
│
├── python/
│   └── load_to_mysql.py                       ← automated ETL loader script
│
├── powerbi/
│   └── SUPPLY_CHAIN.pbix                      ← Power BI dashboard file
│
└── images/
    ├── schema/
    │   ├── star_schema_diagram.png
    │   └── powerbi_model.png
    ├── sql/
    │   ├── revenue_by_product.png
    │   ├── supplier_defect_rate.png
    │   └── supplier_scorecard.png
    └── dashboard/
        ├── 01_executive_summary.png
        ├── 02_supplier_scorecard.png
        ├── 03_quality_control.png
        ├── 04_logistics_analysis.png
        └── 05_inventory_health.png
```

---

## 📊 Dataset Overview

### Raw data (before cleaning)
| Property | Value |
|---|---|
| Total rows | 11,340 |
| Total columns | 24 |
| Issues found | Misnamed columns, negative prices, negative defect rates, mixed case text |

### Normalized schema (after cleaning)

| Table | Type | Rows | Description |
|---|---|---|---|
| products | Dimension | 3 | Product type lookup |
| suppliers | Dimension | 25 | Supplier name and warehouse location |
| carriers | Dimension | 3 | Carrier lookup |
| routes | Dimension | 12 | Shipping route and transport mode |
| orders | Fact | 11,340 | Sales orders with revenue and pricing |
| inventory | Fact | 11,340 | Stock levels and availability |
| logistics | Fact | 11,340 | Shipping cost, quality and defect data |

---

## Part 1 — Excel Data Cleaning and Schema Design

![Star Schema](images/schema/star_schema_diagram.png)

### Problems found in raw data
- 24 columns with generic misnamed headers (`Product type.1`, `Price.1` etc.)
- 7 distinct entities packed into a single flat sheet
- Negative prices, defect rates and shipping costs
- Mixed case text in product type and customer gender columns
- Duplicate and inconsistent supplier entries

### What was done
- Identified and mapped all 24 raw columns to correct semantic names
- Separated 7 distinct entities into individual sheets
- Applied data cleaning rules:
  - Negative prices clipped to 0
  - Negative defect rates clipped to 0
  - Mixed case cleaned with `strip()` and `lower()`
  - Added `data_quality_flag` column to mark dirty rows
- Designed a **star schema** with 4 dimension tables and 3 fact tables
- Added surrogate foreign keys (`product_id`, `supplier_id`, `carrier_id`, `route_id`)
- Built the ERD and schema notes sheet

### Star schema design

```
dim: products   ─┐
dim: suppliers  ─┤
                 ├──► fact: orders ──► fact: inventory
dim: carriers   ─┤              └───► fact: logistics
dim: routes     ─┘
```

---

## Part 2 — Python ETL Pipeline

![Python ETL Success](images/sql/python_etl_output.png)

### Script: `load_to_mysql.py`

Automated loader that reads the Excel schema file and loads all 7 tables into MySQL in the correct FK-safe order.

### How to run

```bash
# Install dependencies
pip install pandas openpyxl sqlalchemy pymysql

# Create the database in MySQL
CREATE DATABASE supply_chain;

# Run the loader
python load_to_mysql.py
```

### What the script does
1. Verifies the Excel file exists in the same folder
2. Connects to MySQL and verifies the connection
3. Reads all 7 sheets from the Excel file
4. Drops existing tables in reverse FK order
5. Creates all tables with correct data types, PKs and FK constraints
6. Loads data in FK-safe order (dimensions first, then facts)
7. Verifies row counts for all 7 tables

### Expected output

```
==========================================
 Supply Chain DB Loader - MySQL/MariaDB
==========================================

  -> Found: SUPPLY_CHAIN_DB_SCHEMA.xlsx
  -> Connecting to MySQL -> localhost:3306/supply_chain
  [OK] Connection successful

  Loading tables...

  [OK] Loaded       3 rows -> products
  [OK] Loaded      25 rows -> suppliers
  [OK] Loaded       3 rows -> carriers
  [OK] Loaded      12 rows -> routes
  [OK] Loaded  11,340 rows -> orders
  [OK] Loaded  11,340 rows -> inventory
  [OK] Loaded  11,340 rows -> logistics

  Verification -- row counts:
  ----------------------------------------
  [OK] products   :       3 rows
  [OK] suppliers  :      25 rows
  [OK] carriers   :       3 rows
  [OK] routes     :      12 rows
  [OK] orders     :  11,340 rows
  [OK] inventory  :  11,340 rows
  [OK] logistics  :  11,340 rows
```

---

## Part 3 — MySQL Database Design

![Power BI Data Model](images/schema/powerbi_model.png)

### Database schema

```sql
-- Dimension tables
products  (product_id PK, product_type)
suppliers (supplier_id PK, supplier_name, warehouse_location)
carriers  (carrier_id PK, carrier)
routes    (route_id PK, shipping_route, transportation_mode)

-- Fact tables
orders    (order_id PK, product_id FK, supplier_id FK,
           carrier_id FK, route_id FK, price, units_sold,
           revenue, customer_gender, order_quantity,
           lead_time_days, data_quality_flag)

inventory (order_id PK FK, product_id FK, supplier_id FK,
           availability, stock_levels)

logistics (order_id PK FK, carrier_id FK, route_id FK,
           shipping_cost, total_logistics_cost,
           manufacturing_lead_time, manufacturing_cost,
           inspection_quantity, inspection_result,
           defect_rate, supplier_rating, quality_score)
```

---

## Part 4 — SQL Analysis

14 queries across 3 difficulty levels.

![Revenue by Product](images/sql/revenue_by_product.png)

### Beginner — single table queries

```sql
-- Q1. Total orders
SELECT COUNT(*) AS total_orders FROM orders;

-- Q2. All product types
SELECT product_id, product_type FROM products;

-- Q3. Orders where price > 80
SELECT order_id, price, revenue
FROM orders
WHERE price > 80
ORDER BY price DESC;

-- Q4. Unique inspection results
SELECT DISTINCT inspection_result FROM logistics;

-- Q5. Orders by customer gender
SELECT customer_gender, COUNT(*) AS total_orders
FROM orders
GROUP BY customer_gender;
```

### Intermediate — joins and aggregations

```sql
-- Q6. Revenue by product type
SELECT p.product_type,
       SUM(o.revenue)    AS total_revenue,
       AVG(o.price)      AS avg_price,
       SUM(o.units_sold) AS total_units
FROM orders o
JOIN products p USING(product_id)
GROUP BY p.product_type
ORDER BY total_revenue DESC;

-- Q7. Supplier with lowest defect rate
SELECT s.supplier_name,
       s.warehouse_location,
       ROUND(AVG(l.defect_rate), 4) AS avg_defect_rate
FROM logistics l
JOIN orders o    USING(order_id)
JOIN suppliers s USING(supplier_id)
GROUP BY s.supplier_name, s.warehouse_location
ORDER BY avg_defect_rate ASC
LIMIT 5;

-- Q8. Shipping cost by transport mode
SELECT r.transportation_mode,
       ROUND(AVG(l.shipping_cost), 2)        AS avg_shipping,
       ROUND(AVG(l.total_logistics_cost), 2) AS avg_total_cost
FROM logistics l
JOIN routes r USING(route_id)
GROUP BY r.transportation_mode
ORDER BY avg_shipping;

-- Q9. Stockout risk orders
SELECT o.order_id,
       o.order_quantity,
       i.stock_levels,
       o.order_quantity - i.stock_levels AS shortage
FROM orders o
JOIN inventory i USING(order_id)
WHERE o.order_quantity > i.stock_levels
ORDER BY shortage DESC;

-- Q10. Inspection results with percentage
SELECT inspection_result,
       COUNT(*) AS total,
       ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS pct
FROM logistics
GROUP BY inspection_result
ORDER BY total DESC;
```

![Supplier Defect Rate](images/sql/supplier_defect_rate.png)

### Advanced — CTEs and window functions

```sql
-- Q11. Rank suppliers by revenue
SELECT s.supplier_name,
       ROUND(SUM(o.revenue), 2) AS total_revenue,
       RANK() OVER (ORDER BY SUM(o.revenue) DESC) AS revenue_rank
FROM orders o
JOIN suppliers s USING(supplier_id)
GROUP BY s.supplier_name
ORDER BY revenue_rank;

-- Q12. Suppliers above average defect rate (CTE)
WITH supplier_defects AS (
  SELECT s.supplier_name,
         AVG(l.defect_rate) AS avg_defect
  FROM logistics l
  JOIN orders o    USING(order_id)
  JOIN suppliers s USING(supplier_id)
  GROUP BY s.supplier_name
),
overall AS (
  SELECT AVG(defect_rate) AS overall_avg FROM logistics
)
SELECT sd.supplier_name,
       ROUND(sd.avg_defect, 4)  AS avg_defect,
       ROUND(o.overall_avg, 4)  AS overall_avg
FROM supplier_defects sd
CROSS JOIN overall o
WHERE sd.avg_defect > o.overall_avg
ORDER BY sd.avg_defect DESC;

-- Q13. Top supplier per warehouse location
WITH ranked AS (
  SELECT s.supplier_name,
         s.warehouse_location,
         ROUND(SUM(o.revenue), 2) AS total_revenue,
         RANK() OVER (
           PARTITION BY s.warehouse_location
           ORDER BY SUM(o.revenue) DESC
         ) AS rnk
  FROM orders o
  JOIN suppliers s USING(supplier_id)
  GROUP BY s.supplier_name, s.warehouse_location
)
SELECT supplier_name, warehouse_location, total_revenue
FROM ranked WHERE rnk = 1
ORDER BY total_revenue DESC;

-- Q14. Full supplier scorecard (capstone query)
SELECT
  s.supplier_name,
  s.warehouse_location,
  ROUND(SUM(o.revenue), 2)                    AS total_revenue,
  ROUND(AVG(l.defect_rate), 4)                AS avg_defect_rate,
  ROUND(AVG(l.quality_score), 2)              AS avg_quality_score,
  ROUND(AVG(o.lead_time_days), 1)             AS avg_lead_time,
  ROUND(AVG(l.manufacturing_cost), 2)         AS avg_mfg_cost,
  SUM(l.inspection_result = 'Pass')           AS pass_count,
  SUM(l.inspection_result = 'Fail')           AS fail_count,
  ROUND(SUM(l.inspection_result = 'Pass')
        * 100.0 / COUNT(*), 1)                AS pass_pct
FROM orders o
JOIN suppliers s  USING(supplier_id)
JOIN logistics l  USING(order_id)
GROUP BY s.supplier_name, s.warehouse_location
ORDER BY total_revenue DESC;
```

![Supplier Scorecard Query](images/sql/supplier_scorecard.png)

---

## Part 5 — Power BI Dashboard

5-page interactive dashboard with **80+ DAX measures**, conditional formatting, drill through, synced slicers and bookmark navigation.

### Page 1 — Executive Summary

![Executive Summary](images/dashboard/01_executive_summary.png)

**Visuals:**
- 5 KPI cards — Total Revenue, Total Orders, Units Sold, Avg Price, Revenue per Order
- Revenue by product type — bar chart
- Revenue by customer gender — column chart
- Revenue share — donut chart
- Revenue by supplier — bar chart with % labels
- Revenue vs target — gauge visual
- 4 synced slicers

**Key DAX measures:**
```dax
Total Revenue = SUM(orders[revenue])
Revenue Share % = DIVIDE([Total Revenue], CALCULATE([Total Revenue], ALL(products))) * 100
Revenue per Order = DIVIDE([Total Revenue], COUNTROWS(orders))
```

---

### Page 2 — Supplier Scorecard

![Supplier Scorecard](images/dashboard/02_supplier_scorecard.png)

**Visuals:**
- 4 KPI cards — Total Suppliers, Best Supplier, Worst Defect Supplier, Avg Rating
- Supplier defect rate ranking — color coded bar chart
- Revenue by supplier — bar chart
- Lead time by warehouse location — column chart
- Full supplier scorecard matrix with conditional formatting
- Supplier risk breakdown — donut chart
- 3 synced slicers

**Key DAX measures:**
```dax
Supplier Revenue Rank = RANKX(ALL(suppliers[supplier_name]), [Total Revenue],, DESC)
Supplier Risk Flag =
VAR Defect = [Avg Defect Rate]
VAR PassR  = [Supplier Pass Rate]
RETURN
SWITCH(TRUE(),
    Defect > 0.08 || PassR < 50, "High Risk",
    Defect > 0.05 || PassR < 65, "Medium Risk",
    "Low Risk"
)
```

---

### Page 3 — Quality Control

![Quality Control](images/dashboard/03_quality_control.png)

**Visuals:**
- 5 KPI cards — Pass Rate %, Fail Rate %, Avg Defect Rate, Avg Quality Score, High Risk Orders
- Inspection results breakdown — column chart
- Defect rate by product type — color coded bar chart
- Quality score by supplier — bar chart
- Quality control matrix — full width with conditional formatting
- Pass rate by location — column chart with 70% target line
- Failed high revenue orders — card and table
- 4 synced slicers

**Key DAX measures:**
```dax
Pass Rate % = DIVIDE([Pass Count], COUNTROWS(logistics)) * 100
Defect Status =
SWITCH(TRUE(),
    [Avg Defect Rate] > 0.08, "High Risk",
    [Avg Defect Rate] > 0.05, "Medium Risk",
    "Low Risk"
)
```

---

### Page 4 — Logistics Analysis

![Logistics Analysis](images/dashboard/04_logistics_analysis.png)

**Visuals:**
- 5 KPI cards — Total Logistics Cost, Avg Shipping Cost, Cheapest Mode, Avg Mfg Lead Time, Slow Orders
- Shipping cost by transport mode — color coded bar chart
- Manufacturing cost by product — column chart
- Route cost comparison — bar chart
- Carrier performance matrix
- Manufacturing lead time by location — column chart
- Logistics cost share by mode — donut chart
- 4 synced slicers

**Key DAX measures:**
```dax
Logistics Cost Ratio = DIVIDE([Total Logistics Cost], [Total Revenue]) * 100
Shipping Cost Status =
SWITCH(TRUE(),
    [Avg Shipping Cost] > Overall * 1.2, "High Cost",
    [Avg Shipping Cost] > Overall,       "Above Avg",
    "Efficient"
)
```

---

### Page 5 — Inventory Health

![Inventory Health](images/dashboard/05_inventory_health.png)

**Visuals:**
- 4 KPI cards — Total Stock, Stockout Risk Orders, Avg Availability, Negative Availability
- Stock levels by product — bar chart
- Stock vs availability by supplier — clustered bar chart
- Stockout risk breakdown — donut chart
- Supplier stock rank — table with conditional formatting
- 3 synced slicers

**Key DAX measures:**
```dax
Stockout Risk Orders =
COUNTROWS(FILTER(inventory, inventory[stock_levels] < 10))

Stock Health Flag =
IF([Stockout Risk %] > 15, "Urgent",
    IF([Stockout Risk %] > 8, "Monitor", "Healthy")
)
```

---

## 🔍 Key Insights

### Revenue
- Total revenue across all orders: **$1,056 — $9,871 per order**
- Price range: **$0 — $104** per unit
- Skincare generates the highest product revenue

### Supplier performance
- 5 suppliers across 5 Indian cities: Mumbai, Delhi, Kolkata, Bangalore, Chennai
- Defect rates range from **0% to 14.9%** — huge variance between suppliers
- Significant quality differences between warehouse locations

### Quality and inspection
- Only **22.9% of orders pass inspection** (2,595 out of 11,340)
- **36.2% fail** (4,102 orders) — high failure rate requiring attention
- **40.9% pending** (4,643 orders) — significant backlog

### Logistics
- 4 transport modes: Road, Air, Rail, Sea
- 3 shipping routes: Route A, Route B, Route C
- Air freight significantly more expensive than road

### Data quality
- Negative shipping costs found and flagged
- Negative defect rates cleaned and clipped to 0
- 24 misnamed columns remapped to correct semantic names

---

## ⚙️ How to Run This Project

### Prerequisites
- Python 3.x
- MySQL / MariaDB
- Power BI Desktop
- Jupyter Notebook (optional)

### Step 1 — Clone the repository
```bash
git clone https://github.com/yourusername/supply-chain-analytics-end-to-end.git
cd supply-chain-analytics-end-to-end
```

### Step 2 — Install Python dependencies
```bash
pip install pandas openpyxl sqlalchemy pymysql
```

### Step 3 — Set up MySQL
```sql
CREATE DATABASE supply_chain;
```

### Step 4 — Update credentials in loader script
```python
# python/load_to_mysql.py
DB_USER     = "your_username"
DB_PASSWORD = "your_password"
DB_NAME     = "supply_chain"
```

### Step 5 — Run the ETL loader
```bash
cd python
python load_to_mysql.py
```

### Step 6 — Run SQL analysis
```
Open sql/02_analysis_queries.sql in MySQL Workbench
Run each query to explore the data
```

### Step 7 — Open Power BI dashboard
```
Open powerbi/SUPPLY_CHAIN.pbix in Power BI Desktop
Refresh the data connection with your MySQL credentials
```

---

## 📸 Screenshots Needed

Upload these screenshots to the `images/` folder:

```
images/schema/
  star_schema_diagram.png     ← ERD sheet from Excel
  powerbi_model.png           ← Power BI Model view (already have this!)

images/sql/
  python_etl_output.png       ← Jupyter notebook showing successful run
  revenue_by_product.png      ← MySQL Workbench Q6 result
  supplier_defect_rate.png    ← MySQL Workbench Q7 result
  supplier_scorecard.png      ← MySQL Workbench Q14 result

images/dashboard/
  01_executive_summary.png    ← Power BI page 1 screenshot
  02_supplier_scorecard.png   ← Power BI page 2 screenshot
  03_quality_control.png      ← Power BI page 3 screenshot
  04_logistics_analysis.png   ← Power BI page 4 screenshot
  05_inventory_health.png     ← Power BI page 5 screenshot
```

---

## 📚 Skills Demonstrated

| Category | Skills |
|---|---|
| Data Engineering | Data cleaning, normalization, star schema design |
| Database | MySQL, relational modeling, PKs and FK constraints |
| Python | pandas, SQLAlchemy, ETL automation, error handling |
| SQL | JOINs, GROUP BY, CTEs, window functions, RANK() |
| Power BI | Data modeling, DAX, conditional formatting, drill through |
| DAX | CALCULATE, RANKX, ALLEXCEPT, SWITCH, DIVIDE, FILTER |
| Business Intelligence | KPI design, dashboard layout, slicer sync, bookmarks |

---

## 👤 Author

**Your Name**
- LinkedIn: [your-linkedin-url]
- GitHub: [your-github-url]
- Email: your@email.com

---

## 📄 License

This project is licensed under the MIT License.
