# QuickBite Analytics — Frontend

React + Vite chat UI for the agentic analytics backend.

## Dev mode

```bash
npm install
npm run dev
```

Open http://localhost:5173/app/ (proxies API calls to http://127.0.0.1:8000)

## Build

```bash
npm run build
```

Built files go to `dist/`. The FastAPI backend serves them at `/app/` when present.

## Environment

Optional `.env` in `frontend/`:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Leave empty when using the Vite dev proxy.
