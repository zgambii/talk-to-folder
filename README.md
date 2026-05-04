# Talk to a Folder

Talk to a Folder is a Google Drive folder assistant. A user connects their Google account, pastes a Drive folder link, and starts asking questions about the files inside that folder.

The app is built around a source-grounded RAG pipeline. It does not treat the LLM as the whole product. The system does the deterministic work first: parse the folder URL, list files, extract text, chunk documents, embed chunks, retrieve relevant context, and only then ask the model to synthesize an answer from the retrieved chunks.

The result is a ChatGPT-style UI built around folder-scoped conversations: paste a folder URL to open a new chat, revisit earlier folders from the sidebar (each restores its thread), and read answers with citations and inspectable retrieved context. For this take-home, conversation history is stored in the browser (localStorage), not on the server.

## Live demo

| Surface | URL |
|--------|-----|
| Frontend | `https://talk-to-folder.vercel.app/` |
| Backend health | `https://talk-to-folder-82xq.onrender.com/health` |

A successful backend health check returns:

```json
{ "status": "ok" }
```

## What it does

You sign in with Google OAuth, paste a Google Drive folder link, and the backend validates the URL, resolves the folder ID, and lists files through the Drive API. Supported files become plain text, split into chunks with reproducible rules, embedded, and stored in a vector store—so later answers are grounded in that folder’s index, not in open-ended model memory.

The chat UI works like a normal assistant: you type a question, the backend pulls the most relevant chunks for that folder only, the model answers strictly from that context, and citations are validated (real chunk IDs, non-empty quotes) before anything is returned.

Supported formats are Google Docs, PDFs, plain text, and Markdown. Anything else is skipped with a clear reason so one bad file never aborts the whole indexing run.

## Repository structure

```text
frontend/
  src/
    api/          # typed API client
    components/   # chat UI, sidebar, citations
    hooks/        # localStorage folder conversations
    types/        # shared API types

backend/
  app/
    api/          # thin FastAPI routes and dependencies
    domain/       # folder, document, and chat services/models
    integrations/ # Google OAuth, Drive listing, extraction
    ai/           # embeddings, prompts, answer generation, vector protocol
    storage/      # Chroma and Supabase vector-store implementations
  migrations/
    001_vector_store.sql
```

## High-leverage extension

The base prompt asks for a user to paste a Drive folder link and chat with the files. I extended that into a more complete folder-chat product:

- **ChatGPT/Claude-style folder conversations** — The UI is organized around persistent folder chats instead of a one-off question form.
- **Previous folder sidebar** — Users can return to previously indexed folders and continue asking questions in that folder’s context.
- **Citations plus retrieved context** — User-facing citations are separated from the retrieved chunks/debug context so the system remains inspectable.
- **Production vector-store path** — Local development uses Chroma for speed, while deployment uses Supabase pgvector behind the same `VectorStore` interface.
- **Citation validation** — The backend rejects model citations that do not map to retrieved chunks, which prevents fake provenance from reaching the UI.

## Architecture (text diagram)

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Browser (Vercel)                                │
│  React + TS + Vite  │  OAuth redirect to backend  │  localStorage (chats)   │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │ HTTPS (credentials, CORS allowlist)
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FastAPI (Render)                                     │
│  Session cookie  │  Auth routes  │  Folder index  │  Chat (RAG)           │
│       │                 │                │                  │                │
│       └─────────────────┴────────────────┴──────────────────┘                │
│                         │                         │                          │
│              Google OAuth + Drive API          OpenAI embeddings + answers   │
└─────────────────────────┬─────────────────────────┬────────────────────────┘
                          │                         │
          ┌───────────────┴──────────────┐          │
          ▼                              ▼          ▼
   Google Drive                   ┌──────────────┐  OpenAI API
   (files, export, download)      │ Vector store │  (embeddings + JSON answer)
                                  └──────┬───────┘
                                         │
                    ┌────────────────────┴────────────────────┐
                    ▼                                         ▼
            Chroma (local disk)                    Supabase Postgres + pgvector
            VECTOR_STORE_PROVIDER=chroma         VECTOR_STORE_PROVIDER=supabase
```

## RAG pipeline (step by step)

1. **Folder URL → folder ID** — The pasted link is normalized and parsed with `urllib.parse` (no LLM): host must be `drive.google.com`; folder ID comes from path (`/drive/folders/<id>`) or open-folder query patterns. Invalid URLs fail fast with a clear error.

2. **Drive listing** — With the user’s OAuth token, the backend calls the Drive API for the folder’s children (and resolves the folder’s display name).

3. **Supported file detection** — Only types the extractor handles are processed (Google Docs, PDF, plain text, Markdown). Others are recorded as skipped with reasons.

4. **Text extraction** — Docs export / PDF parsing / text reads produce a single document body per file. Extraction failures are skipped per file so one bad file does not block the folder.

5. **Deterministic chunking** — Extracted text is split into `DocumentChunk` records with stable rules (same input → same chunks and IDs).

6. **Embeddings** — Chunk texts are embedded in batch with the configured OpenAI embedding model (default `text-embedding-3-small`).

7. **Vector upsert** — Chunks and embeddings are written via the `VectorStore` interface; re-indexing deletes the folder’s old vectors first.

8. **Question-time retrieval** — The user message is embedded; **folder-scoped** similarity search returns the top-*k* chunks (default *k* = 8).

9. **Answer generation** — A structured prompt includes only those chunks. The model must return **JSON** matching `FolderAnswer` (answer, confidence, citations).

10. **Citation validation** — After Pydantic parses the JSON, the server checks every `citation.chunk_id` is in the retrieved set and that quotes are non-empty. Mismatch → error instead of silently trusting the model.

11. **Response to client** — The API returns the answer, citations, and the retrieved chunks so the UI can show sources transparently.

## Why deterministic code runs before LLM calls

- **Folder identity** must be exact; guessing or “interpreting” URLs would mix folders or leak data. Parsing is pure string/URL logic with explicit validation.

- **Chunking and IDs** define what “a source” is for citations. If chunk boundaries drifted randomly, the same document could get incompatible IDs between indexing and chat, breaking citation checks and user trust.

- **Cost and latency** — Avoiding an LLM for steps that are rules-based keeps indexing predictable and cheaper.

- **Testability** — URL parsing, chunking, and validation are unit-testable without nondeterministic model output.

## Why citations are validated

Models can **hallucinate** citations or point at chunks that were never retrieved. The backend only has evidence for the chunks returned from the vector store. Requiring `chunk_id` ∈ retrieved set and non-empty quotes:

- Surfaces model mistakes as **hard failures** (or regeneration policy later) instead of showing fake provenance.

- Keeps the **UI honest**: displayed citations always correspond to real retrieved segments.

- Aligns the product story with **grounded** answers: the citation set is a subset of actual context.


## Vector store tradeoffs

| Aspect | **Chroma (local)** | **Supabase pgvector (deployed)** |
|--------|--------------------|----------------------------------|
| **Ops** | Embedded process, path on disk (`CHROMA_PATH`). No external DB. | Managed Postgres; needs migration and service role key on the server only. |
| **Persistence** | Fine for dev; disk on a single machine. | Durable, backup-friendly, fits serverless/restarty hosting. |
| **Scale** | Good for take-home and single-node demos. | Better story for concurrent users and larger corpora (with tuning). |
| **Config** | `VECTOR_STORE_PROVIDER=chroma` | `VECTOR_STORE_PROVIDER=supabase` + `SUPABASE_*` |

**`VectorStore` protocol** (`app/ai/vector_store.py`): a small interface (`upsert_chunks`, `search`, `delete_folder`) implemented by `ChromaVectorStore` and `SupabaseVectorStore`. Folder indexing and chat depend on the protocol, not on a specific database — swapping providers is an env-driven wiring change in `app/api/dependencies.py`.

## Local setup

### Prerequisites

- **Node.js** 20.19+, 22.13+, or 24+ (see `frontend/package.json` engines).
- **Python** 3.12+.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
# Edit .env: VITE_API_BASE_URL=http://localhost:8000
npm run dev
```

Vite serves the app (default `http://localhost:5173`).

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install ".[dev]"        # runtime + pytest, ruff, black; or pip install . for runtime only
cp .env.example .env
# Fill in secrets and URLs (see Environment variables)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Install from **`pyproject.toml`** as above; `[dev]` extras are required for the testing and lint commands below.

### Environment variables

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

Run **frontend and backend in two terminals** during development.

## Supabase migration

1. Create a [Supabase](https://supabase.com) project.
2. Open **SQL Editor** and run the script: **`backend/migrations/001_vector_store.sql`**.
3. That script: enables the **`vector`** extension; creates **`document_chunks`** with an **ivfflat** index on embeddings; defines **`match_document_chunks`** RPC used for cosine-style retrieval.
4. In the Supabase dashboard, copy **Project URL** → `SUPABASE_URL`, and **service role** key → `SUPABASE_SERVICE_ROLE_KEY` (backend env only).
5. Set `VECTOR_STORE_PROVIDER=supabase` on the backend.

Embedding width in the migration is **1536** — keep it aligned with the embedding model dimensions you use.

## Google Cloud OAuth setup

1. **Create or select a Google Cloud project.**

2. **Enable the Google Drive API**  
   APIs & Services → Library → “Google Drive API” → Enable.

3. **Configure OAuth consent screen**  
   User type **External** is typical for demos. Add app name, support email, scopes.

4. **Add OAuth scope**  
   Add **`https://www.googleapis.com/auth/drive.readonly`** (Drive read-only).

5. **Create OAuth client**  
   Credentials → Create credentials → **OAuth client ID** → Application type **Web application**.

6. **Authorized redirect URIs** (must match `GOOGLE_REDIRECT_URI` exactly)  
   - Local: `http://localhost:8000/api/auth/google/callback`  
   - Production: `https://<your-render-host>/api/auth/google/callback`

7. **Authorized JavaScript origins** (if required by your flow)  
   - Local: `http://localhost:5173`  
   - Production: `https://<your-vercel-host>`

8. **Testing mode and test users**  
   While the OAuth app is in **Testing**, only **test users** listed on the consent screen can sign in. Add reviewer Google accounts there so they can complete the take-home flow.

9. **Copy Client ID and Client Secret** into backend env (`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`).

## Deployment

### Backend (Render)

- **Root directory:** `backend`
- **Build command:** `pip install .`  
  (This repo’s `render.yaml` uses `pip install -e .`; either installs the package from `pyproject.toml`.)
- **Start command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Python:** 3.12+
- Set **`ENVIRONMENT=production`** so session cookies work cross-site with the Vercel frontend (`Secure`, `SameSite=None`).
- Set **`FRONTEND_URL`** to the exact Vercel origin (CORS + cookies).
- Production **`GOOGLE_REDIRECT_URI`** must be the Render callback URL registered in Google Cloud.

### Frontend (Vercel)

- **Root directory:** `frontend`
- Framework preset: **Vite** (usually auto-detected).
- **Environment variable:** `VITE_API_BASE_URL=https://<your-render-service>.onrender.com`

### Supabase in production

Use **`VECTOR_STORE_PROVIDER=supabase`** with migration applied and secrets set as in [Supabase migration](#supabase-migration).

## Testing and quality commands

**Backend** (from `backend/` with venv active and dev install):

```bash
pytest
ruff check .
black --check .
```

**Frontend** (from `frontend/`):

```bash
npm run lint
npm run build
npm run format:check    # Prettier check
npm run format          # Prettier write
```

## Tradeoffs (intentional for this take-home)

- **Chat history in localStorage** — Fast to ship, no account DB; clearing the browser or switching devices drops history; not suitable for sensitive or multi-device production use without a server store.

- **OAuth app in Testing mode** — Reviewers must be **test users**; app may take some time until it is published through Google Console.

- **Limited file types** — Google Docs, PDF, plain text, Markdown only; Sheets, Slides, and images, and are out of scope (doable implementation as they only need custom extractors).

- **No background indexing worker** — Indexing runs in the HTTP request path; large folders increase latency and risk timeouts on cheap hosting.

## Potential future improvements

- **Server-side chat persistence** — Postgres or Supabase tables for threads, messages, and auditability.
- **Background indexing jobs** — Queue (e.g. Redis + worker) for large folders, progress webhooks or polling.
- **Folder refresh detection** — Drive `modifiedTime` / revision checks to invalidate or delta-update chunks.
- **Reranking and retrieval thresholds** — Cross-encoder or LLM rerank; minimum similarity to reduce irrelevant chunks.
- **Sheets / Slides** — Structured or slide-per-slide extraction pipelines.
- **Streaming responses** — Token streaming for perceived latency (with care for citation consistency).

---

Thank you for your time! This was a thought-provoking and enjoyable take home to work on. I was able to use my prior experiences but also learned a few things along the way.
