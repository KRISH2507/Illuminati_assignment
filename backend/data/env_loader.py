"""Load environment variables from project root .env."""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"


def load_project_env() -> Path:
    """Load .env from project root regardless of current working directory."""
    load_dotenv(ENV_FILE, override=False)
    return ENV_FILE
