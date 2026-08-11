"""Shared agent state and helpers."""

from __future__ import annotations

import json
import re
from typing import Annotated, Any, TypedDict

import operator


class AgentState(TypedDict):
    question: str
    date_context: str
    orchestration: str
    plan: str
    sql: str
    query_result: list[dict[str, Any]]
    sql_error: str
    retry_count: int
    answer: str
    steps: Annotated[list[dict[str, str]], operator.add]


def extract_sql(text: str) -> str:
    """Extract SQL from a markdown code block or raw text."""
    match = re.search(r"```sql\s*(.*?)```", text, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()

    match = re.search(r"```\s*(SELECT[\s\S]*?)```", text, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()

    stripped = text.strip()
    if stripped.upper().startswith("SELECT") or stripped.upper().startswith("WITH"):
        return stripped.rstrip(";")

    raise ValueError("No SQL query found in analyst response.")


def extract_json_block(text: str) -> dict[str, Any]:
    """Best-effort JSON extraction from LLM output."""
    text = text.strip()

    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text, re.IGNORECASE)
    if fence:
        text = fence.group(1).strip()

    decoder = json.JSONDecoder()
    try:
        obj, _ = decoder.raw_decode(text)
        if isinstance(obj, dict):
            return obj
    except json.JSONDecodeError:
        pass

    start = text.find("{")
    if start == -1:
        raise ValueError("No JSON object found in response.")

    obj, _ = decoder.raw_decode(text[start:])
    if not isinstance(obj, dict):
        raise ValueError("Expected a JSON object in response.")
    return obj


def append_step(agent: str, action: str, output: str) -> list[dict[str, str]]:
    return [{"agent": agent, "action": action, "output": output}]
