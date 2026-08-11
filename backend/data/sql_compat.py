"""SQL compatibility helpers for DuckDB and PostgreSQL."""

from __future__ import annotations

import re


def adapt_sql_for_postgres(sql: str) -> str:
    """
    PostgreSQL ROUND() requires numeric, not double precision.
    Rewrite ROUND(expr, n) -> ROUND(CAST(expr AS NUMERIC), n).
    """
    pattern = re.compile(
        r"ROUND\s*\(\s*([^()]+(?:\([^)]*\)[^()]*)*)\s*,\s*(\d+)\s*\)",
        re.IGNORECASE,
    )
    previous = None
    adapted = sql
    while adapted != previous:
        previous = adapted
        adapted = pattern.sub(r"ROUND(CAST(\1 AS NUMERIC), \2)", adapted)
    return adapted
