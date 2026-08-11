"""Shared data loading and view definitions."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

DATA_SHEETS = [
    "Store_Master",
    "Product_Master",
    "Customer_Master",
    "Promotions",
    "Calendar",
    "Orders",
    "Order_Details",
    "Glossary",
]

VIEW_DDL_STATEMENTS = [
    """
    CREATE OR REPLACE VIEW v_orders_enriched AS
    SELECT
        o.order_id,
        o.order_datetime,
        CAST(o.order_datetime AS DATE) AS order_date,
        o.store_id,
        s.store_name,
        s.city,
        s.state,
        s.region,
        s.store_format,
        s.performance_factor,
        o.customer_id,
        o.channel,
        o.total_qty,
        o.gross_bill_value,
        o.discount_amount,
        o.promo_id,
        o.net_before_tax,
        o.tax_amount,
        o.net_revenue,
        c.year,
        c.month,
        c.month_no,
        c.day_name,
        c.day_type,
        c.festive_period
    FROM orders o
    LEFT JOIN store_master s ON o.store_id = s.store_id
    LEFT JOIN calendar c ON CAST(o.order_datetime AS DATE) = c.date
    """,
    """
    CREATE OR REPLACE VIEW v_order_lines AS
    SELECT
        od.order_detail_id,
        od.order_id,
        od.sku_id,
        p.sku_name,
        p.category,
        p.veg_nonveg,
        od.quantity,
        od.unit_price,
        od.line_gross_value,
        od.line_discount,
        od.line_net_value,
        od.est_cogs,
        o.order_datetime,
        CAST(o.order_datetime AS DATE) AS order_date,
        o.channel,
        o.net_revenue AS order_net_revenue,
        o.store_id,
        s.store_name,
        s.city,
        s.region
    FROM order_details od
    JOIN orders o ON od.order_id = o.order_id
    JOIN product_master p ON od.sku_id = p.sku_id
    LEFT JOIN store_master s ON o.store_id = s.store_id
    """,
]


def normalize_table_name(sheet_name: str) -> str:
    return sheet_name.lower()


def clean_dataframe(df: pd.DataFrame, sheet_name: str) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned.columns = [str(col).lower() for col in cleaned.columns]

    for col in cleaned.select_dtypes(include="object").columns:
        cleaned[col] = cleaned[col].where(cleaned[col].notna(), None)

    if sheet_name == "Orders":
        for col in ("customer_id", "promo_id"):
            if col in cleaned.columns:
                cleaned[col] = cleaned[col].where(cleaned[col].notna(), None)

    return cleaned


def load_excel_sheets(excel_path: Path) -> dict[str, pd.DataFrame]:
    if not excel_path.exists():
        raise FileNotFoundError(f"Dataset not found: {excel_path}")

    xl = pd.ExcelFile(excel_path)
    missing = [s for s in DATA_SHEETS if s not in xl.sheet_names]
    if missing:
        raise ValueError(f"Missing sheets in workbook: {missing}")

    frames: dict[str, pd.DataFrame] = {}
    for sheet in DATA_SHEETS:
        df = pd.read_excel(xl, sheet_name=sheet)
        frames[normalize_table_name(sheet)] = clean_dataframe(df, sheet)

    return frames
