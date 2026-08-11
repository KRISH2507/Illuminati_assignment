"""Database connection helpers — DuckDB (local) or PostgreSQL (deploy)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import duckdb

from backend.config import get_settings
from backend.data.sql_compat import adapt_sql_for_postgres

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "qsr.duckdb"

_FORBIDDEN_SQL = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|REPLACE|ATTACH|COPY|GRANT|REVOKE)\b",
    re.IGNORECASE,
)


def get_db_backend() -> str:
    """Return 'postgres' when DATABASE_URL is set, otherwise 'duckdb'."""
    if get_settings().database_url:
        return "postgres"
    return "duckdb"


def get_db_path() -> Path:
    return DEFAULT_DB_PATH


def database_ready() -> bool:
    backend = get_db_backend()
    if backend == "postgres":
        try:
            rows = run_query("SELECT COUNT(*) AS n FROM orders")
            return rows[0]["n"] > 0
        except Exception:
            return False
    return DEFAULT_DB_PATH.exists()


def _validate_sql(sql: str) -> str:
    normalized = sql.strip().rstrip(";")
    if not normalized.upper().startswith("SELECT") and not normalized.upper().startswith("WITH"):
        raise ValueError("Only SELECT/WITH queries are allowed.")
    if _FORBIDDEN_SQL.search(normalized):
        raise ValueError("Query contains forbidden SQL keywords.")
    return normalized


def _rows_to_dicts(columns: list[str], rows: list[tuple[Any, ...]]) -> list[dict]:
    return [dict(zip(columns, row)) for row in rows]


def run_query(sql: str, db_path: Path | None = None) -> list[dict]:
    """Execute a read-only SQL query and return rows as dicts."""
    normalized = _validate_sql(sql)

    if get_db_backend() == "postgres":
        normalized = adapt_sql_for_postgres(normalized)
        return _run_postgres_query(normalized)

    path = db_path or DEFAULT_DB_PATH
    if not path.exists():
        raise FileNotFoundError(
            f"Database not found at {path}. Run: python scripts/seed_db.py"
        )

    conn = duckdb.connect(str(path), read_only=True)
    try:
        result = conn.execute(normalized)
        columns = [desc[0].lower() for desc in result.description]
        rows = result.fetchall()
        return _rows_to_dicts(columns, rows)
    finally:
        conn.close()


def _run_postgres_query(sql: str) -> list[dict]:
    import psycopg
    from psycopg.rows import dict_row

    database_url = get_settings().database_url
    if not database_url:
        raise ValueError("DATABASE_URL is not configured.")

    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
            return [{k.lower(): v for k, v in row.items()} for row in rows]


def get_table_names(db_path: Path | None = None) -> list[str]:
    if get_db_backend() == "postgres":
        rows = run_query(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_type IN ('BASE TABLE', 'VIEW')
            ORDER BY table_name
            """
        )
        return [row["table_name"] for row in rows]

    path = db_path or DEFAULT_DB_PATH
    conn = duckdb.connect(str(path), read_only=True)
    try:
        result = conn.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'main' ORDER BY table_name"
        ).fetchall()
        return [row[0] for row in result]
    finally:
        conn.close()
