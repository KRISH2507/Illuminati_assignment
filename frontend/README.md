# QuickBite Analytics — Frontend

React + Vite chat UI for the agentic analytics backend.

## Dev mode

```bash
npm install
npm run dev
```

Open http://localhost:5173/ (backend must run on port 8000)

## Vercel deploy

| Setting | Value |
|---------|-------|
| Root Directory | `frontend` |
| Build Command | `npm run build` |
| Output Directory | `dist` |
| Install Command | `npm install` |

**Environment variable:**

| Key | Value |
|-----|-------|
| `VITE_API_URL` | `https://illuminati-assignment.onrender.com` |

Local dev: leave `VITE_API_URL` empty (uses proxy to localhost:8000).
Production: set `VITE_API_URL` to your Render backend URL.

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
