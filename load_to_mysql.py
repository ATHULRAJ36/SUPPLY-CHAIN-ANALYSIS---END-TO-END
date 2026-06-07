"""
Supply Chain DB Loader -- MySQL / MariaDB
==========================================
Requirements:
    pip install pandas openpyxl sqlalchemy pymysql

Usage:
    1. Place this script in the SAME folder as SUPPLY_CHAIN_DB_SCHEMA.xlsx
    2. In Jupyter run:
           import os
           os.chdir(r"C:\\path\\to\\your\\folder")
           !python load_to_mysql.py
"""

import sys
import os
import pandas as pd
from sqlalchemy import create_engine, text

# --- CONFIG ------------------------------------------------------------------
DB_HOST     = "localhost"
DB_PORT     = 3306
DB_USER     = "root"
DB_PASSWORD = "athul2003"
DB_NAME     = "supply_chain"    # must already exist: CREATE DATABASE supply_chain;

EXCEL_FILE  = "SUPPLY_CHAIN_DB_SCHEMA.xlsx"
# -----------------------------------------------------------------------------

# Exact sheet names in the Excel file (confirmed)
SHEET_TO_TABLE = {
    "products":  "products",
    "suppliers": "suppliers",
    "carriers":  "carriers",
    "routes":    "routes",
    "orders":    "orders",
    "inventory": "inventory",
    "logistics": "logistics",
}

# Load order: lookup tables MUST come before fact tables (FK safety)
LOAD_ORDER = ["products", "suppliers", "carriers", "routes",
              "orders", "inventory", "logistics"]

CREATE_STATEMENTS = {
    "products": """
        CREATE TABLE IF NOT EXISTS products (
            product_id   INT         NOT NULL,
            product_type VARCHAR(50) NOT NULL,
            PRIMARY KEY (product_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    "suppliers": """
        CREATE TABLE IF NOT EXISTS suppliers (
            supplier_id        INT          NOT NULL,
            supplier_name      VARCHAR(50)  NOT NULL,
            warehouse_location VARCHAR(100),
            PRIMARY KEY (supplier_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    "carriers": """
        CREATE TABLE IF NOT EXISTS carriers (
            carrier_id INT         NOT NULL,
            carrier    VARCHAR(50) NOT NULL,
            PRIMARY KEY (carrier_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    "routes": """
        CREATE TABLE IF NOT EXISTS routes (
            route_id            INT         NOT NULL,
            shipping_route      VARCHAR(20) NOT NULL,
            transportation_mode VARCHAR(20) NOT NULL,
            PRIMARY KEY (route_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    "orders": """
        CREATE TABLE IF NOT EXISTS orders (
            order_id          INT           NOT NULL,
            product_id        INT,
            supplier_id       INT,
            carrier_id        INT,
            route_id          INT,
            price             DECIMAL(10,2),
            units_sold        INT,
            revenue           DECIMAL(12,2),
            customer_gender   VARCHAR(10),
            order_quantity    INT,
            lead_time_days    INT,
            data_quality_flag TINYINT       DEFAULT 0,
            PRIMARY KEY (order_id),
            FOREIGN KEY (product_id)  REFERENCES products(product_id),
            FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
            FOREIGN KEY (carrier_id)  REFERENCES carriers(carrier_id),
            FOREIGN KEY (route_id)    REFERENCES routes(route_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    "inventory": """
        CREATE TABLE IF NOT EXISTS inventory (
            order_id     INT NOT NULL,
            product_id   INT,
            supplier_id  INT,
            availability INT,
            stock_levels INT,
            PRIMARY KEY (order_id),
            FOREIGN KEY (order_id)    REFERENCES orders(order_id),
            FOREIGN KEY (product_id)  REFERENCES products(product_id),
            FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    "logistics": """
        CREATE TABLE IF NOT EXISTS logistics (
            order_id                INT NOT NULL,
            carrier_id              INT,
            route_id                INT,
            shipping_cost           DECIMAL(10,2),
            total_logistics_cost    DECIMAL(12,2),
            manufacturing_lead_time INT,
            manufacturing_cost      DECIMAL(10,2),
            inspection_quantity     INT,
            inspection_result       VARCHAR(10),
            defect_rate             DECIMAL(6,4),
            supplier_rating         INT,
            quality_score           DECIMAL(8,4),
            PRIMARY KEY (order_id),
            FOREIGN KEY (order_id)   REFERENCES orders(order_id),
            FOREIGN KEY (carrier_id) REFERENCES carriers(carrier_id),
            FOREIGN KEY (route_id)   REFERENCES routes(route_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
}

# Drop order must be reverse of load order (child tables first)
DROP_ORDER = ["logistics", "inventory", "orders",
              "routes", "carriers", "suppliers", "products"]


def log(msg, status="info"):
    icons = {"info": "->", "ok": "[OK]", "warn": "[!]", "err": "[ERR]"}
    print(f"  {icons.get(status, '-')} {msg}")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    # -- 1. Verify Excel file -------------------------------------------------
    script_dir = os.path.dirname(os.path.abspath(__file__))
    excel_path = os.path.join(script_dir, EXCEL_FILE)
    if not os.path.exists(excel_path):
        log(f"Excel file not found at: {excel_path}", "err")
        log("Make sure SUPPLY_CHAIN_DB_SCHEMA.xlsx is in the same folder as this script.", "warn")
        sys.exit(1)
    log(f"Found: {excel_path}")

    # -- 2. Connect to MySQL --------------------------------------------------
    conn_str = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    )
    log(f"Connecting to MySQL -> {DB_HOST}:{DB_PORT}/{DB_NAME}")
    try:
        engine = create_engine(conn_str, echo=False)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        log("Connection successful", "ok")
    except Exception as e:
        log(f"Connection failed: {e}", "err")
        log("Check credentials or run: CREATE DATABASE supply_chain; in MySQL", "warn")
        sys.exit(1)

    # -- 3. Read Excel --------------------------------------------------------
    log("Reading Excel file...")
    xl = pd.ExcelFile(excel_path)
    available_sheets = xl.sheet_names
    log(f"Sheets detected: {available_sheets}")

    # -- 4. Drop existing tables (child first) --------------------------------
    print()
    log("Dropping existing tables (if any)...")
    with engine.begin() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        for table in DROP_ORDER:
            conn.execute(text(f"DROP TABLE IF EXISTS `{table}`;"))
            log(f"Dropped: {table}")
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))

    # -- 5. Create tables and load data ---------------------------------------
    print()
    log("Creating tables and loading data...")
    print()

    with engine.begin() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))

        for table in LOAD_ORDER:
            # Find matching sheet (exact match or sheet name contains table name)
            matched = None
            for sheet in available_sheets:
                if sheet.lower().strip() == table or table in sheet.lower():
                    matched = sheet
                    break

            if not matched:
                log(f"No sheet found for table '{table}' -- skipping", "warn")
                continue

            # Read sheet (header=1 skips the title row in row 0)
            df = pd.read_excel(excel_path, sheet_name=matched, header=1)
            df.dropna(how="all", inplace=True)
            df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
            df = df.loc[:, ~df.columns.str.startswith("unnamed")]

            log(f"Sheet '{matched}' -> table '{table}' | columns: {list(df.columns)}")

            # Create table
            conn.execute(text(CREATE_STATEMENTS[table]))

            # Load data
            df.to_sql(
                name=table,
                con=conn,
                if_exists="append",
                index=False,
                chunksize=500,
                method="multi",
            )
            log(f"Loaded {len(df):,} rows -> {table}", "ok")

        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))

    # -- 6. Verify row counts -------------------------------------------------
    print()
    print("  Verification -- row counts:")
    print("  ----------------------------------------")
    with engine.connect() as conn:
        for table in LOAD_ORDER:
            try:
                count = conn.execute(text(f"SELECT COUNT(*) FROM `{table}`;")).scalar()
                log(f"{table:12s}: {count:>7,} rows", "ok")
            except Exception as e:
                log(f"{table}: {e}", "err")

    print()
    print("  ==========================================")
    print("   All done! Database is ready to query.")
    print("  ==========================================")
    print()
    print("  Sample queries:")
    print("  ----------------------------------------")
    print("  -- Revenue by product type")
    print("  SELECT p.product_type, SUM(o.revenue) AS total_revenue")
    print("  FROM orders o JOIN products p USING(product_id)")
    print("  GROUP BY p.product_type;")
    print()
    print("  -- Defect rate by supplier")
    print("  SELECT s.supplier_name, AVG(l.defect_rate) AS avg_defect")
    print("  FROM logistics l JOIN suppliers s USING(supplier_id)")
    print("  GROUP BY s.supplier_name ORDER BY avg_defect DESC;")
    print()
    print("  -- Shipping cost by transport mode")
    print("  SELECT r.transportation_mode, AVG(l.shipping_cost) AS avg_shipping")
    print("  FROM logistics l JOIN routes r USING(route_id)")
    print("  GROUP BY r.transportation_mode;")


if __name__ == "__main__":
    print()
    print("  ==========================================")
    print("   Supply Chain DB Loader - MySQL/MariaDB  ")
    print("  ==========================================")
    print()
    main()
