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

## Documentation

Detail lives in `docs/` so this README stays a short entry point

| Doc | What it covers |
|-----|----------------|
| [Architecture & RAG](docs/architecture.md) | System diagram, pipeline steps, deterministic vs LLM work, citation checks, vector store tradeoffs and `VectorStore` protocol |
| [Local setup](docs/setup.md) | Prerequisites, install/run, environment variables |
| [Deployment](docs/deployment.md) | Supabase migration, Google OAuth, Render, Vercel |
| [Development](docs/development.md) | `pytest`, Ruff, Black, frontend lint/build/Prettier |
| [Tradeoffs & roadmap](docs/tradeoffs.md) | Intentional limits of the take-home and possible next steps |

---

Thank you for your time! This was a thought-provoking and enjoyable take home to work on. I was able to use my prior experiences but also learned a few things along the way.
