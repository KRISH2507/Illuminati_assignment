# Deployment Guide

## Stack

| Layer | Local | Deploy |
|-------|-------|--------|
| Frontend | Vite dev / `frontend/dist` | Built static files at `/app/` |
| Backend | FastAPI + Uvicorn | Render / Railway / Fly.io |
| Database | DuckDB file | **PostgreSQL** (Neon, Supabase, Render Postgres) |
| LLM | Groq (free) | Groq API key in env |

## Environment variables (production)

```env
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_key_here
GROQ_MODEL=llama-3.3-70b-versatile
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

Render and Railway auto-set `DATABASE_URL` when you attach a Postgres addon.

## Option A — Deploy on Render

### 1. PostgreSQL
Create a **PostgreSQL** instance on Render. Copy the **Internal Database URL**.

### 2. Web Service
- **Build command:**
  ```bash
  pip install -r requirements.txt && cd frontend && npm install && npm run build
  ```
- **Start command:**
  ```bash
  python scripts/seed_postgres.py && uvicorn backend.main:app --host 0.0.0.0 --port $PORT
  ```
- **Environment:**
  - `LLM_PROVIDER=groq`
  - `GROQ_API_KEY=...`
  - `DATABASE_URL=...` (from Render Postgres)

### 3. Open app
`https://your-app.onrender.com/app/`

## Option B — Local PostgreSQL (test deploy setup)

```bash
# Start Postgres
docker compose up -d

# .env
DATABASE_URL=postgresql://quickbite:quickbite@localhost:5432/quickbite
LLM_PROVIDER=groq
GROQ_API_KEY=your_key

# Seed + run
pip install -r requirements.txt
python scripts/seed_postgres.py
uvicorn backend.main:app --reload
```

## Option C — Local DuckDB (no Postgres)

Leave `DATABASE_URL` empty in `.env`:

```bash
python scripts/seed_db.py
uvicorn backend.main:app --reload
```

## Verify deployment

```bash
curl https://your-app.onrender.com/health
```

Expected:
```json
{
  "database_present": true,
  "db_backend": "postgres",
  "agents_ready": true,
  "llm_provider": "groq"
}
```

## Notes

- **Not RAG** — no vector DB needed for deploy
- Re-run `seed_postgres.py` if you reset the database
- Groq free tier has rate limits — fine for demo/submission
- For Gemini deploy: set `LLM_PROVIDER=gemini` and add `langchain-google-genai`
