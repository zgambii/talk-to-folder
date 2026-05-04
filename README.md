# Talk to Folder

Monorepo scaffold for a React + TypeScript + Vite frontend and a Python FastAPI backend.

No product features are implemented yet. The current code is only a clean development baseline.

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
