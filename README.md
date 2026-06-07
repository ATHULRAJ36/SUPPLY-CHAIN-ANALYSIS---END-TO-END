# 🚚 Supply Chain Analytics — End to End Project

> **Complete analytics pipeline:** Raw Excel data → Data Cleaning → MySQL Database → SQL Analysis → Power BI Dashboard

---

## 📌 Project Overview

A full end-to-end supply chain analytics project built on a real-world dataset of **11,340 orders** across **5 suppliers**, **3 product types**, **4 transportation modes** and **5 warehouse locations** across India.

The project covers every stage of the analytics pipeline — from a messy, misnamed raw Excel file to a 4-page interactive Power BI dashboard with 20+ DAX measures.

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

## Part 1 — Excel Data Cleaning 

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

---

## Part 2 — Python ETL Pipeline

![Python ETL Success](https://github.com/ATHULRAJ36/SUPPLY-CHAIN-ANALYSIS---END-TO-END/blob/main/PYTHON%20ETL%20SUCCESS.png)

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
## Part 3 — MySQL Database Design

### What I built
A fully normalized relational database with 7 tables, proper primary keys, foreign key constraints and correct data types for every column.

### What I learned

**Database design concepts:**
- What normalization means and why it matters
- Difference between dimension tables and fact tables
- How to design a star schema for analytics
- How to define primary keys and foreign keys
- Why foreign key constraints prevent bad data
- How to choose correct data types — DECIMAL for money, INT for quantities, VARCHAR for text

**SQL concepts learned and applied:**

| Concept | What I used it for |
|---|---|
| CREATE TABLE | Built all 7 tables with correct structure |
| PRIMARY KEY | Uniquely identified every row in every table |
| FOREIGN KEY | Linked fact tables to dimension tables |
| REFERENCES | Connected orders to products, suppliers, carriers, routes |
| ENGINE=InnoDB | Enabled foreign key support in MySQL |
| DROP TABLE IF EXISTS | Safely dropped tables before reloading |
| SET FOREIGN_KEY_CHECKS | Managed FK constraints during bulk operations |

**Data types I used:**

| Type | Used for |
|---|---|
| INT | IDs, quantities, stock levels, lead times |
| DECIMAL(10,2) | Prices, shipping costs, manufacturing costs |
| DECIMAL(12,2) | Revenue (larger range needed) |
| DECIMAL(6,4) | Defect rates (small decimal precision) |
| DECIMAL(8,4) | Quality scores |
| VARCHAR(10) | Short text — gender, inspection result |
| VARCHAR(50) | Medium text — product type, supplier name |
| VARCHAR(100) | Longer text — warehouse location |
| TINYINT | Boolean flag — data_quality_flag (0 or 1) |

---

## Part 4 — SQL Analysis

### What I learned

**Basic SQL — single table:**

| Concept | What I used it for |
|---|---|
| SELECT | Retrieve data from tables |
| FROM | Specify which table to query |
| WHERE | Filter rows by condition |
| ORDER BY | Sort results ascending or descending |
| GROUP BY | Group rows to aggregate data |
| COUNT() | Count total rows or orders |
| SUM() | Add up revenue and costs |
| AVG() | Calculate average prices and defect rates |
| ROUND() | Format decimal numbers cleanly |
| DISTINCT | Get unique values from a column |
| LIMIT | Return only top N results |

**Intermediate SQL — multi table:**

| Concept | What I used it for |
|---|---|
| JOIN | Connected orders to products, suppliers, routes |
| USING() | Cleaner JOIN syntax when column names match |
| Multiple JOINs | Linked 3 and 4 tables in a single query |
| Aliases (o, p, s, l) | Shortened table names for readability |
| Aggregate + JOIN | Combined SUM and AVG across joined tables |
| HAVING | Filtered grouped results after aggregation |

**Advanced SQL — window functions and CTEs:**

| Concept | What I used it for |
|---|---|
| RANK() | Ranked suppliers by revenue and defect rate |
| OVER() | Defined the window for ranking functions |
| PARTITION BY | Reset ranking within each warehouse location |
| ORDER BY inside OVER | Controlled ranking direction |
| WITH (CTE) | Broke complex queries into readable steps |
| CROSS JOIN | Combined CTE results with overall averages |
| Subqueries | Used inside WHERE and SELECT clauses |
| Window SUM | Calculated percentage of total in one query |

**Analysis topics covered:**
- Revenue breakdown by product type and supplier
- Defect rate ranking across all 5 suppliers
- Shipping cost comparison by transport mode
- Stockout risk orders where demand exceeds stock
- Inspection pass, fail and pending breakdown with percentages
- Top supplier per warehouse location using PARTITION BY
- Suppliers above average defect rate using CTE
- Full supplier scorecard combining all 5 tables in one query

---

## Part 5 — Power BI Dashboard

5-page interactive dashboard with **DAX measures**, conditional formatting, drill through, synced slicers and bookmark navigation.

## MODEL VIEW
![MODEL VIEW](https://github.com/ATHULRAJ36/SUPPLY-CHAIN-ANALYSIS---END-TO-END/blob/main/MODEL%20VIEW.png)

### Page 1 — Executive Summary

![Executive Summary](https://github.com/ATHULRAJ36/SUPPLY-CHAIN-ANALYSIS---END-TO-END/blob/main/EXECUTIVE%20SUMMERY.png)

**Visuals:**
- 4 KPI  cards — Total Revenue, Total Orders, Units Sold, Total Stock Level
- Revenue by product type — bar chart
- Revenue by customer gender — column chart
- Revenue share — donut chart
- 3 synced slicers

**Key DAX measures:**
```dax
Total Revenue = SUM(orders[revenue])
Revenue Share % = DIVIDE([Total Revenue], CALCULATE([Total Revenue], ALL(products))) * 100
Revenue per Order = DIVIDE([Total Revenue], COUNTROWS(orders))
```

---

### Page 2 — Supplier Scorecard

![Supplier Scorecard](https://github.com/ATHULRAJ36/SUPPLY-CHAIN-ANALYSIS---END-TO-END/blob/main/SUPPLIER%20SCORECARD.png)

**Visuals:**
- 3 KPI cards — Total Suppliers, Best Supplier, Avg Rating
- quality score vs Defect rate
- Avg logistic cost by supplier
- Lead time by warehouse location 
- Lead time by suppliers
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
### Page 3 — Logistics Analysis

![Logistics Analysis](https://github.com/ATHULRAJ36/SUPPLY-CHAIN-ANALYSIS---END-TO-END/blob/main/LOGISTIC%20ANALYSIS.png)

**Visuals:**
- 4 KPI cards — Total Logistics Cost, Avg Defect rate, Total Manufacturing rate, Total shipping Cost
- Shipping cost by transport mode — color coded bar chart
- Manufacturing cost by product — column chart
- Route comparison — bar chart
- Logistics cost by product
- 3 synced slicers

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

### Page 4 — Inventory Health

![Inventory Health](https://github.com/ATHULRAJ36/SUPPLY-CHAIN-ANALYSIS---END-TO-END/blob/main/INVENTORY%20HEALTH.png)

**Visuals:**
- 3 KPI cards — Total Stock, Stockout Risk Orders, Avg Availability
- Stock levels by product 
- Stock vs availability by supplier
- Stock level by Location
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
  
### Logistics
- 4 transport modes: Road, Air, Rail, Sea
- 3 shipping routes: Route A, Route B, Route C
- Air freight significantly more expensive than road

### Data quality
- Negative shipping costs found and flagged
- Negative defect rates cleaned and clipped to 0
- 24 misnamed columns remapped to correct semantic names
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
