"""PostgreSQL seeding logic."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine, text

from backend.config import get_settings
from backend.data.seed_common import VIEW_DDL_STATEMENTS, load_excel_sheets

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw" / "QSR_Agentic_Insights_Dataset.xlsx"


def seed_postgres(database_url: str | None = None, excel_path: Path = DATA_RAW) -> None:
    url = database_url or get_settings().database_url
    if not url:
        raise ValueError("DATABASE_URL is not set.")

    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    frames = load_excel_sheets(excel_path)
    engine = create_engine(url)

    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
        conn.execute(text("GRANT ALL ON SCHEMA public TO public"))

        for table_name, df in frames.items():
            df.to_sql(
                table_name,
                conn,
                if_exists="replace",
                index=False,
                method="multi",
                chunksize=1000,
            )

        for stmt in VIEW_DDL_STATEMENTS:
            conn.execute(text(stmt))
