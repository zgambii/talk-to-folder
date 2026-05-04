# Architecture & RAG

[← README](../README.md)

## Architecture

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
