"""FastAPI entry point for the QuickBite Agentic Analytics API."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from backend.data.env_loader import load_project_env

load_project_env()

from backend.agents.graph import run_analytics_question
from backend.analytics.reference_queries import (
    REFERENCE_QUESTIONS,
    get_example_questions,
    get_store_decline_question,
)
from backend.analytics.store_decline import analyze_declining_stores
from backend.config import get_settings
from backend.data.db import database_ready, get_db_backend, get_table_names, run_query
from backend.data.schema import get_schema_text
from backend.models import AgentStep, AskRequest, AskResponse
from backend.startup import bootstrap_database

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw" / "QSR_Agentic_Insights_Dataset.xlsx"
DATA_DB = PROJECT_ROOT / "data" / "qsr.duckdb"
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_settings.cache_clear()
    try:
        bootstrap_database()
    except Exception as exc:
        logger.error("Database bootstrap failed: %s", exc)
    yield


app = FastAPI(
    title="QuickBite Agentic Analytics",
    description="Natural-language QSR business insights powered by agentic AI",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    settings = get_settings()
    return {
        "service": "QuickBite Agentic Analytics",
        "status": "ok",
        "version": "1.0.0",
        "ui": "/app/",
        "docs": "/docs",
        "health": "/health",
        "agents_ready": settings.agents_ready(),
        "db_backend": get_db_backend(),
        "database_ready": database_ready(),
    }


@app.head("/")
def root_head():
    return Response(status_code=200)


@app.head("/health")
def health_head():
    return Response(status_code=200)


@app.get("/health")
def health():
    settings = get_settings()
    db_stats = None
    if database_ready():
        try:
            tables = get_table_names()
            date_range = run_query(
                "SELECT MIN(order_datetime) AS min_date, MAX(order_datetime) AS max_date FROM orders"
            )
            db_stats = {
                "backend": get_db_backend(),
                "tables": tables,
                "date_range": date_range[0] if date_range else None,
            }
        except Exception as exc:
            db_stats = {"backend": get_db_backend(), "error": str(exc)}

    return {
        "status": "healthy",
        "dataset_present": DATA_RAW.exists(),
        "database_present": database_ready(),
        "db_backend": get_db_backend(),
        "agents_ready": settings.agents_ready(),
        "llm_provider": settings.llm_provider,
        "model": settings.active_model(),
        "dataset_path": str(DATA_RAW),
        "database_path": str(DATA_DB) if get_db_backend() == "duckdb" else "postgresql",
        "database": db_stats,
    }


def _require_database():
    if not database_ready():
        backend = get_db_backend()
        if backend == "postgres":
            detail = "PostgreSQL not seeded. Run: python scripts/seed_postgres.py"
        else:
            detail = "Database not seeded. Run: python scripts/seed_db.py"
        raise HTTPException(status_code=503, detail=detail)


@app.get("/schema")
def schema():
    _require_database()
    return {"schema": get_schema_text()}


@app.get("/examples")
def examples():
    items = get_example_questions()
    items.append(get_store_decline_question())
    return {"questions": items}


@app.get("/benchmarks")
def benchmarks():
    _require_database()
    results = []
    for item in REFERENCE_QUESTIONS:
        try:
            rows = item.run()
            results.append({"id": item.id, "question": item.question, "rows": rows})
        except Exception as exc:
            results.append({"id": item.id, "question": item.question, "error": str(exc)})

    try:
        decline_rows = analyze_declining_stores()
        q8 = get_store_decline_question()
        results.append(
            {
                "id": q8["id"],
                "question": q8["question"],
                "rows": decline_rows,
            }
        )
    except Exception as exc:
        q8 = get_store_decline_question()
        results.append(
            {"id": q8["id"], "question": q8["question"], "error": str(exc)}
        )

    return {"benchmarks": results}


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    _require_database()
    settings = get_settings()
    if not settings.agents_ready():
        raise HTTPException(
            status_code=503,
            detail=(
                f"LLM not configured for provider '{settings.llm_provider}'. "
                "Add the matching API key to .env (see .env.example)."
            ),
        )

    try:
        result = run_analytics_question(request.question)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return AskResponse(
        question=result["question"],
        answer=result["answer"],
        sql=result.get("sql") or None,
        data=result.get("data", []),
        steps=[AgentStep(**step) for step in result.get("steps", [])],
        plan=result.get("plan") or None,
        orchestration=result.get("orchestration") or None,
    )


if FRONTEND_DIST.exists():
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/app")
    def serve_app():
        return FileResponse(FRONTEND_DIST / "index.html")

    @app.get("/app/{path:path}")
    def serve_app_paths(path: str):
        file_path = FRONTEND_DIST / path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIST / "index.html")
