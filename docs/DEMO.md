# Demo Guide — QuickBite Agentic Analytics

## Prerequisites

1. Python deps installed: `pip install -r requirements.txt`
2. Database seeded: `python scripts/seed_db.py`
3. `.env` contains `OPENAI_API_KEY=...`
4. Frontend built or running in dev mode

## Start the demo

### Terminal 1 — Backend

```bash
cd "d:\D files\illuminity_project"
uvicorn backend.main:app --reload
```

### Terminal 2 — Frontend (dev)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173/app/

### Production-style (single backend)

```bash
cd frontend
npm install
npm run build
cd ..
uvicorn backend.main:app --reload
```

Open http://127.0.0.1:8000/app/

## 5-minute demo script

1. **Intro (30s)**  
   Show the UI and explain the flow:  
   `User Question → Orchestrator → Planner → Analyst → Insight Writer`

2. **Health check (15s)**  
   Point to status pills: DB Ready, Agents Live.

3. **Question 1 — KPI summary (1 min)**  
   Click **Q1** or ask:  
   *"What were the total revenue, orders, and average order value for the last 3 months?"*  
   Highlight agent trace, SQL, and business answer.

4. **Question 2 — Rankings (1 min)**  
   Ask: *"Which are the top 5 and bottom 5 stores by revenue?"*  
   Show data table with store rankings.

5. **Question 8 — Decline diagnosis (1.5 min)**  
   Click **Q8** or ask:  
   *"Which stores have consistently declined in the last 3 months, and what are the key reasons?"*  
   Explain the dedicated decline-analysis agent path.

6. **Architecture wrap-up (45s)**  
   Mention:
   - DuckDB for structured analytics (no RAG)
   - Read-only SQL tools
   - Source code in `backend/agents/` and `backend/analytics/`
   - Validation script: `python scripts/validate_questions.py`

## All 8 supported questions

| ID | Question |
|----|----------|
| Q1 | Total revenue, orders, and AOV for the last 3 months |
| Q2 | Top 5 and bottom 5 stores by revenue |
| Q3 | Revenue and AOV by channel |
| Q4 | Top 5 SKUs by quantity and revenue |
| Q5 | Cities with revenue decline over the last 3 months |
| Q6 | Weekend vs weekday performance |
| Q7 | Festive vs normal period performance |
| Q8 | Stores with consistent decline and key reasons |

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `database_present: false` | Run `python scripts/seed_db.py` |
| `Agents Need API Key` | Add `OPENAI_API_KEY` to `.env` and restart backend |
| Frontend cannot reach API | Start backend on port 8000; use Vite dev proxy |
| SQL errors in trace | Agent auto-retries up to 3 times; re-ask with a clearer question |

## Submission checklist

- [ ] Source code included (`backend/`, `frontend/`, `scripts/`)
- [ ] README with setup steps
- [ ] Architecture doc (`docs/ARCHITECTURE.md`)
- [ ] Demo video or live walkthrough
- [ ] `.env.example` included (no real API keys committed)
