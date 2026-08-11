"""
Load QSR Excel dataset into DuckDB (local development).

Usage:
    python scripts/seed_db.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import duckdb

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.data.seed_common import VIEW_DDL_STATEMENTS, load_excel_sheets

DATA_RAW = PROJECT_ROOT / "data" / "raw" / "QSR_Agentic_Insights_Dataset.xlsx"
DATA_DB = PROJECT_ROOT / "data" / "qsr.duckdb"


def seed_database(excel_path: Path = DATA_RAW, db_path: Path = DATA_DB) -> None:
    frames = load_excel_sheets(excel_path)

    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    conn = duckdb.connect(str(db_path))
    try:
        for table_name, df in frames.items():
            conn.register("staging_df", df)
            conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM staging_df")
            conn.unregister("staging_df")

        for stmt in VIEW_DDL_STATEMENTS:
            conn.execute(stmt)
    finally:
        conn.close()


def print_summary(db_path: Path = DATA_DB) -> None:
    conn = duckdb.connect(str(db_path), read_only=True)
    try:
        print("\n=== Tables loaded ===")
        tables = conn.execute(
            "SELECT table_name, table_type FROM information_schema.tables "
            "WHERE table_schema = 'main' ORDER BY table_type, table_name"
        ).fetchall()
        for name, table_type in tables:
            count = conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
            print(f"  {name} ({table_type}): {count:,} rows")

        print("\n=== Date range ===")
        row = conn.execute(
            "SELECT MIN(order_datetime), MAX(order_datetime) FROM orders"
        ).fetchone()
        print(f"  Orders: {row[0]} to {row[1]}")
    finally:
        conn.close()


def main() -> int:
    print(f"Loading: {DATA_RAW}")
    print(f"Target:  {DATA_DB}")

    try:
        seed_database()
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print("Database seeded successfully.")
    print_summary()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
