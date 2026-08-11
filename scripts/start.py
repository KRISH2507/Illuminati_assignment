"""Launch script for local and production."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.data.env_loader import load_project_env

load_project_env()


def main() -> int:
    from backend.config import get_settings
    from backend.startup import bootstrap_database

    get_settings.cache_clear()
    print(f"Project root: {PROJECT_ROOT}")

    settings = get_settings()
    print(f"LLM provider: {settings.llm_provider}")
    print(f"Agents ready: {settings.agents_ready()}")
    print(f"DB backend: {settings.db_backend()}")

    try:
        bootstrap_database()
        print("Database bootstrap: OK")
    except Exception as exc:
        print(f"Database bootstrap warning: {exc}")

    # Render/cloud always sets PORT — bind to 0.0.0.0 so the port is reachable externally
    on_cloud = "PORT" in os.environ
    port = os.environ.get("PORT", "8000")
    host = os.environ.get("HOST", "0.0.0.0" if on_cloud else "127.0.0.1")
    reload = os.environ.get("DEV", "0" if on_cloud else "1") == "1"

    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "backend.main:app",
        "--host",
        host,
        "--port",
        str(port),
    ]
    if reload:
        cmd.append("--reload")

    print(f"Starting backend at http://{host}:{port} (reload={reload})")
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
