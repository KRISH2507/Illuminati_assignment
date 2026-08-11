# Agent Architecture

## Flow

```
User Question
    ↓
Orchestrator Agent      ← routes the question, coordinates workflow
    ↓
Query Planner Agent     ← maps NL → tables, metrics, time windows
    ↓
Data Analyst Agent      ← runs SQL / analytics tools against DuckDB
    ↓
Insight Writer Agent    ← turns results into business narrative
    ↓
Response to User
```

## Agent roles

| Agent | Responsibility |
|-------|----------------|
| **Orchestrator** | Parse intent, select workflow, manage retries |
| **Query Planner** | Identify required tables, filters, aggregations |
| **Data Analyst** | Execute read-only SQL, return structured data |
| **Insight Writer** | Summarize findings with business context |

## Tools (Phase 3 — done)

| Tool | Purpose |
|------|---------|
| `get_schema()` | Table/column descriptions for the LLM |
| `get_date_context()` | Max date in data, "last 3 months" window |
| `list_tables()` | Available tables and views |
| `run_sql(query)` | Read-only SQL execution on DuckDB |

## API (Phase 3–4)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ask` | POST | Run full agent workflow on a business question |
| `/examples` | GET | List all 8 supported business questions |
| `/benchmarks` | GET | Reference SQL results (no LLM required) |
| `/schema` | GET | Schema metadata |
| `/health` | GET | Service and database status |

## Supported questions (Phase 4 — validated)

Reference SQL and benchmarks are in `backend/analytics/reference_queries.py`.
Store decline diagnostics (Q8) use a dedicated analytics path in `backend/analytics/store_decline.py`.

## Why not RAG / vectors?

This project is **agentic SQL analytics**, not Retrieval-Augmented Generation.

| Approach | Used here? | Why |
|----------|------------|-----|
| SQL on structured tables | Yes | Accurate aggregations, joins, rankings |
| LLM for planning + SQL generation | Yes | Natural language → query → insight |
| Vector DB / embeddings | No | Data is tabular, not unstructured text |
| Semantic search | No | Questions map to metrics, not document similarity |

The assignment explicitly expects agents that **query and analyze data with code/SQL** — not uploading the dataset into ChatGPT.

## Database: DuckDB vs PostgreSQL

| | DuckDB (current) | PostgreSQL |
|--|------------------|------------|
| **Local dev** | Perfect — single file, zero setup | Needs install + server |
| **This use case** | Ideal for read-only analytics on 20K rows | Overkill locally |
| **Deployment** | Ship `qsr.duckdb` with the app | Use managed Postgres if scaling |
| **Submission** | Fully acceptable | Not required |

Everything runs locally today. PostgreSQL is optional only if you deploy to cloud and want a shared managed DB.

- Source: Excel → DuckDB (`data/qsr.duckdb`)
- Seed script: `python scripts/seed_db.py`
- Enriched views: `v_orders_enriched`, `v_order_lines`
- Schema API: `GET /schema`
- No vector DB / RAG — structured SQL analytics only (see note below)

## Tech stack

- **Backend:** Python, FastAPI
- **Database:** DuckDB
- **Agents:** LangGraph / LangChain
- **LLM:** OpenAI (configurable via `.env`)
- **Frontend:** TBD (Streamlit or React)
