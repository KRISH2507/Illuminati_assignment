"""CLI helper to test the agent pipeline."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

from backend.agents.graph import run_analytics_question


def main() -> int:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Ask a QuickBite analytics question")
    parser.add_argument("question", nargs="?", help="Business question in natural language")
    args = parser.parse_args()

    question = args.question or "What were the total revenue, orders, and average order value for the last 3 months?"
    print(f"Question: {question}\n")

    try:
        result = run_analytics_question(question)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print("=== Agent Steps ===")
    for step in result["steps"]:
        print(f"[{step['agent']}] {step['action']}")
        print(step["output"])
        print()

    print("=== SQL ===")
    print(result.get("sql") or "(none)")
    print()

    print("=== Answer ===")
    print(result["answer"])
    print()

    print("=== Data Preview ===")
    print(json.dumps(result.get("data", [])[:5], indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
