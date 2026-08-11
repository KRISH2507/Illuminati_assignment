"""Pydantic models for API requests and responses."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, examples=["What were total revenue and orders in the last 3 months?"])


class AgentStep(BaseModel):
    agent: str
    action: str
    output: str


class AskResponse(BaseModel):
    question: str
    answer: str
    sql: str | None = None
    data: list[dict[str, Any]] = Field(default_factory=list)
    steps: list[AgentStep] = Field(default_factory=list)
    plan: str | None = None
    orchestration: str | None = None
