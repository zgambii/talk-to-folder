# Local setup

[← README](../README.md)

## Prerequisites

- **Node.js** 20.19+, 22.13+, or 24+ (see `frontend/package.json` engines).
- **Python** 3.12+.

## Frontend

```bash
cd frontend
npm install
cp .env.example .env
# Edit .env: VITE_API_BASE_URL=http://localhost:8000
npm run dev
```

Vite serves the app (default `http://localhost:5173`).

## Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install ".[dev]"        # runtime + pytest, ruff, black; or pip install . for runtime only
cp .env.example .env
# Fill in secrets and URLs (see below)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Install from **`pyproject.toml`** as above; `[dev]` extras are required for lint and test commands (see [Development](development.md)).

Run **frontend and backend in two terminals** during development.

## Environment variables

**Backend** (`backend/.env.example` — copy to `backend/.env`):

| Variable | Purpose |
|----------|---------|
| `ENVIRONMENT` | `development` vs `production` (session cookie `Secure` / `SameSite=None` in prod). |
| `FRONTEND_URL` | Frontend origin for redirects and CORS (e.g. `http://localhost:5173`). |
| `FRONTEND_ORIGIN` | Optional extra allowed CORS origin. |
| `SESSION_SECRET_KEY` | Secret for signed session cookies. |
| `SESSION_COOKIE_NAME` | Cookie name (default `talk_to_folder_session`). |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | OAuth client. |
| `GOOGLE_REDIRECT_URI` | Must match Google Cloud console (e.g. `http://localhost:8000/api/auth/google/callback`). |
| `OPENAI_API_KEY` | OpenAI API key. |
| `OPENAI_EMBEDDING_MODEL` | Default `text-embedding-3-small`. |
| `OPENAI_ANSWER_MODEL` or `OPENAI_CHAT_MODEL` | Answer model (config reads `OPENAI_CHAT_MODEL` first, then `OPENAI_ANSWER_MODEL`; default `gpt-4.1-mini`). |
| `VECTOR_STORE_PROVIDER` | `chroma` (default) or `supabase`. |
| `CHROMA_PATH` | Local Chroma directory (default `.chroma`). |
| `SUPABASE_URL` / `SUPABASE_SERVICE_ROLE_KEY` | Required when `VECTOR_STORE_PROVIDER=supabase`. **Server only** — never expose in the browser. |

**Frontend** (`frontend/.env.example`):

| Variable | Purpose |
|----------|---------|
| `VITE_API_BASE_URL` | Backend base URL (e.g. `http://localhost:8000`). |

For production hosting, OAuth, and Supabase, see [Deployment](deployment.md).
