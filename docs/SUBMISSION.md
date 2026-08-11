# Submission checklist — QuickBite Agentic Analytics

## Submission readiness: ~95%

You are **very close** to a complete submission. Code and infra are done.

### Done (ready to submit)

- [x] Working prototype (backend + frontend + agents)
- [x] Source code with agent roles and orchestration
- [x] PostgreSQL (Neon) connected and seeded — 20,000 orders
- [x] Groq LLM configured and working
- [x] All 8 required analytics questions validated on Postgres
- [x] Agent trace visible in UI
- [x] SQL + data table shown (auditable)
- [x] Auto-seed on deploy startup (`backend/startup.py`)
- [x] Render deploy config (`render.yaml`)
- [x] Architecture doc (`docs/ARCHITECTURE.md`)
- [x] Demo script (`docs/DEMO.md`)
- [x] Deploy guide (`docs/DEPLOY.md`)
- [x] **Not RAG** — agentic SQL analytics (correct for assignment)

### You still need (~30–60 min)

- [ ] Push code to **GitHub** (never commit `.env`)
- [ ] Deploy on **Render** using `render.yaml`
- [ ] Set env vars on Render: `GROQ_API_KEY`, `DATABASE_URL`, `LLM_PROVIDER=groq`
- [ ] Test live URL — Q1 and Q8 in the UI
- [ ] Record **3–5 min demo video** or prepare live walkthrough
- [ ] Submit: repo link + live URL + demo on the form

## Your `.env` layout (correct)

```env
LLM_PROVIDER=groq
GROQ_API_KEY=...
GROQ_MODEL=llama-3.3-70b-versatile

DATABASE_URL=postgresql://...@...neon.tech/neondb?sslmode=require
```

When `DATABASE_URL` is set, the app uses **Neon Postgres** automatically.  
When empty, it falls back to local **DuckDB**.

## Deploy steps (Render)

1. Push repo to GitHub
2. Render → New Web Service → connect repo
3. Use `render.yaml` or set:
   - **Build:** `pip install -r requirements.txt && cd frontend && npm install && npm run build`
   - **Start:** `python scripts/start.py`
4. Add environment variables (copy from `.env`, not the file itself)
5. First boot auto-seeds Postgres if empty
6. Open `https://your-app.onrender.com/app/`

## Verify locally before deploy

```bash
python scripts/start.py
# Open http://127.0.0.1:8000/health
# Open http://127.0.0.1:8000/app/
```

Expected health:
```json
{
  "database_present": true,
  "db_backend": "postgres",
  "agents_ready": true,
  "llm_provider": "groq"
}
```

## Security reminder

- **Never commit `.env`** to GitHub (already in `.gitignore`)
- If keys were ever exposed, rotate Groq and Neon passwords
