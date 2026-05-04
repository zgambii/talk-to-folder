# Talk to Folder

React + TypeScript + Vite frontend and Python FastAPI backend for a Google Drive folder RAG app.

## Project Structure

```text
.
├── frontend/   # React, TypeScript, Vite, ESLint, Prettier
└── backend/    # FastAPI, Ruff, Black
```

## Prerequisites

- Node.js 20.19+, 22.13+, or 24+
- Python 3.12+

## Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Useful commands:

```bash
npm run lint
npm run format
npm run build
```

## Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
uvicorn app.main:app --reload
```

Production start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Useful commands:

```bash
pytest
ruff check .
black --check .
```

### Vector Store

Local development uses Chroma by default:

```env
VECTOR_STORE_PROVIDER=chroma
CHROMA_PATH=.chroma
```

For a deployed Supabase Postgres + pgvector store:

```env
VECTOR_STORE_PROVIDER=supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

Run `backend/migrations/001_vector_store.sql` in the Supabase SQL editor before switching providers. The migration enables `pgvector`, creates the `document_chunks` table, adds indexes, and defines the `match_document_chunks` RPC used by the backend.

Keep `SUPABASE_SERVICE_ROLE_KEY` on the backend only. Never expose it in frontend environment variables or browser code.

## Local Development

Run the frontend and backend in separate terminals. By default, the frontend expects the backend at `http://localhost:8000`.

```bash
# Terminal 1
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2
cd frontend
npm run dev
```

For local Google OAuth, add this authorized redirect URI in Google Cloud:

```text
http://localhost:8000/api/auth/google/callback
```

## Deployment

### Supabase Setup

1. Create a Supabase project.
2. Run `backend/migrations/001_vector_store.sql` in the Supabase SQL editor.
3. Copy the project URL into `SUPABASE_URL`.
4. Copy the service role key into `SUPABASE_SERVICE_ROLE_KEY` on the backend only.
5. Set `VECTOR_STORE_PROVIDER=supabase` in production.

### Render Backend

This repo includes `render.yaml` for a simple Render Blueprint. It deploys the `backend/` directory, installs dependencies from `pyproject.toml`, and starts FastAPI with:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

If configuring Render manually:

```text
Root Directory: backend
Build Command: pip install -e .
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Use Python 3.12+ and set `ENVIRONMENT=production` so cookies use `Secure` and `SameSite=None` for the Vercel frontend to call the Render API with credentials.

### Vercel Frontend

Create a Vercel project with `frontend/` as the project root. Vercel can infer Vite, so no `vercel.json` is required.

Set:

```env
VITE_API_BASE_URL=https://your-render-service.onrender.com
```

### Google OAuth

For local development, keep:

```env
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
FRONTEND_URL=http://localhost:5173
```

For production, add this authorized redirect URI in Google Cloud:

```text
https://your-render-service.onrender.com/api/auth/google/callback
```

Then set the backend environment:

```env
GOOGLE_REDIRECT_URI=https://your-render-service.onrender.com/api/auth/google/callback
FRONTEND_URL=https://your-vercel-project.vercel.app
```

### Environment Checklist

Backend:

```env
ENVIRONMENT=production
FRONTEND_URL=https://your-vercel-project.vercel.app
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=https://your-render-service.onrender.com/api/auth/google/callback
SESSION_SECRET_KEY=...
SESSION_COOKIE_NAME=talk_to_folder_session
OPENAI_API_KEY=...
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_CHAT_MODEL=gpt-4.1-mini
VECTOR_STORE_PROVIDER=supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=...
```

Frontend:

```env
VITE_API_BASE_URL=https://your-render-service.onrender.com
```

### Common Deployment Issues

- OAuth returns `Google OAuth is not configured.`: verify `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and `GOOGLE_REDIRECT_URI` are set on Render.
- OAuth redirects fail: make sure the exact production callback URL is registered in Google Cloud.
- Browser requests fail with CORS: set `FRONTEND_URL` to the exact Vercel origin and avoid wildcard origins because cookies require `allow_credentials=true`.
- Login works but later API calls are unauthorized: confirm `ENVIRONMENT=production`, HTTPS URLs, frontend `credentials: include`, and that the browser is not blocking third-party cookies.
- Supabase retrieval fails: run `backend/migrations/001_vector_store.sql` and confirm `VECTOR_STORE_PROVIDER=supabase`, `SUPABASE_URL`, and `SUPABASE_SERVICE_ROLE_KEY`.
