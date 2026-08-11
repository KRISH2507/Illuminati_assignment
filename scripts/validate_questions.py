"""Validate reference analytics questions against DuckDB."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.analytics.reference_queries import REFERENCE_QUESTIONS, get_store_decline_question
from backend.analytics.store_decline import analyze_declining_stores
from backend.data.db import get_db_path


def main() -> int:
    db_path = get_db_path()
    if not db_path.exists():
        print(f"Database missing: {db_path}. Run: python scripts/seed_db.py", file=sys.stderr)
        return 1

    print("QuickBite Analytics — Reference Question Validation\n")
    failures = 0

    for item in REFERENCE_QUESTIONS:
        print(f"[{item.id}] {item.question}")
        try:
            rows = item.run()
            print(f"  OK — {len(rows)} row(s)")
            print(json.dumps(rows[:3], indent=2, default=str))
            if not rows:
                print("  WARN — empty result set")
        except Exception as exc:
            failures += 1
            print(f"  FAIL — {exc}")
        print()

    q8 = get_store_decline_question()
    print(f"[{q8['id']}] {q8['question']}")
    try:
        rows = analyze_declining_stores()
        print(f"  OK — {len(rows)} declining store(s)")
        preview = [
            {
                "store_id": r["store_id"],
                "store_name": r["store_name"],
                "declining_months": r["declining_months"],
                "key_reasons": r.get("key_reasons", [])[:2],
            }
            for r in rows[:3]
        ]
        print(json.dumps(preview, indent=2, default=str))
        if not rows:
            print("  WARN — no declining stores found")
    except Exception as exc:
        failures += 1
        print(f"  FAIL — {exc}")

    print()
    if failures:
        print(f"Validation finished with {failures} failure(s).")
        return 1

    print("All reference questions validated successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
