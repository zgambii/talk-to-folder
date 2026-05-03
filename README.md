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

## Local Development

Run the frontend and backend in separate terminals. By default, the frontend expects the backend at `http://localhost:8000`.
