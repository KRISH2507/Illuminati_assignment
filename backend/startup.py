"""Application startup helpers for deployment."""

from __future__ import annotations

import logging
from pathlib import Path

from backend.config import get_settings
from backend.data.db import database_ready, get_db_backend, run_query

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw" / "QSR_Agentic_Insights_Dataset.xlsx"


def bootstrap_database() -> None:
    """Seed PostgreSQL on first deploy when DATABASE_URL is set but tables are empty."""
    settings = get_settings()
    if not settings.database_url:
        logger.info("DATABASE_URL not set — using local DuckDB if available.")
        return

    if database_ready():
        logger.info("PostgreSQL already seeded.")
        return

    if not DATA_RAW.exists():
        raise FileNotFoundError(
            f"Dataset missing at {DATA_RAW}. Cannot seed PostgreSQL on startup."
        )

    logger.info("Seeding PostgreSQL (first deploy)...")
    from backend.data.postgres_seed import seed_postgres

    seed_postgres()
    rows = run_query("SELECT COUNT(*) AS n FROM orders")
    logger.info("PostgreSQL seeded — orders: %s", rows[0]["n"])


def get_startup_status() -> dict:
    settings = get_settings()
    return {
        "db_backend": get_db_backend(),
        "database_ready": database_ready(),
        "agents_ready": settings.agents_ready(),
        "llm_provider": settings.llm_provider,
        "model": settings.active_model(),
    }
