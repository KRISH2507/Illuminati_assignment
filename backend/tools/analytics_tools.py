"""LangChain tools for data analysis."""

from __future__ import annotations

import json

from langchain_core.tools import tool

from backend.data.db import get_table_names, run_query
from backend.data.schema import get_schema_text


@tool
def get_schema() -> str:
    """Return database schema, relationships, and metric definitions."""
    return get_schema_text()


@tool
def get_date_context() -> str:
    """Return dataset date bounds and the last-3-months analysis window."""
    rows = run_query(
        """
        WITH bounds AS (
            SELECT
                MIN(CAST(order_datetime AS DATE)) AS min_date,
                MAX(CAST(order_datetime AS DATE)) AS max_date
            FROM orders
        )
        SELECT
            min_date,
            max_date,
            max_date - INTERVAL '3 months' AS last_3m_start,
            max_date AS last_3m_end
        FROM bounds
        """
    )
    return json.dumps(rows[0], default=str)


@tool
def list_tables() -> str:
    """List all tables and views available in the database."""
    return json.dumps(get_table_names())


@tool
def run_sql(query: str) -> str:
    """Execute a read-only SQL SELECT/WITH query against DuckDB and return JSON rows."""
    rows = run_query(query)
    return json.dumps(rows, default=str)


ANALYTICS_TOOLS = [get_schema, get_date_context, list_tables, run_sql]
