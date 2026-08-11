"""Seed PostgreSQL from CLI."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import get_settings
from backend.data.db import run_query
from backend.data.postgres_seed import DATA_RAW, seed_postgres


def print_summary() -> None:
    print("\n=== PostgreSQL tables loaded ===")
    tables = run_query(
        """
        SELECT table_name, table_type
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_type, table_name
        """
    )
    for row in tables:
        count = run_query(f"SELECT COUNT(*) AS n FROM {row['table_name']}")[0]["n"]
        print(f"  {row['table_name']} ({row['table_type']}): {count:,} rows")

    date_range = run_query(
        "SELECT MIN(order_datetime) AS min_date, MAX(order_datetime) AS max_date FROM orders"
    )[0]
    print(f"\n=== Date range ===\n  Orders: {date_range['min_date']} to {date_range['max_date']}")


def main() -> int:
    settings = get_settings()
    if not settings.database_url:
        print("Error: DATABASE_URL is not set in .env", file=sys.stderr)
        return 1

    print(f"Loading: {DATA_RAW}")
    host_part = settings.database_url.split("@")[-1] if "@" in settings.database_url else "postgres"
    print(f"Target:  PostgreSQL ({host_part})")

    try:
        seed_postgres()
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print("PostgreSQL seeded successfully.")
    print_summary()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
