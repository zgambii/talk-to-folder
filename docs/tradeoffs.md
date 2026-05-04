# Tradeoffs & roadmap

[← README](../README.md)

## Tradeoffs (intentional for this take-home)

- **Chat history in localStorage** — Fast to ship, no account DB; clearing the browser or switching devices drops history; not suitable for sensitive or multi-device production use without a server store.

- **OAuth app in Testing mode** — Reviewers must be **test users**; publishing the app through Google Console takes extra time.

- **Limited file types** — Google Docs, PDF, plain text, and Markdown only. Sheets, Slides, images, and other binaries are out of scope until custom extractors exist.

- **No background indexing worker** — Indexing runs in the HTTP request path; large folders increase latency and risk timeouts on cheap hosting.

## Potential future improvements

- **Server-side chat persistence** — Postgres or Supabase tables for threads, messages, and auditability.
- **Background indexing jobs** — Queue (e.g. Redis + worker) for large folders, progress webhooks or polling.
- **Folder refresh detection** — Drive `modifiedTime` / revision checks to invalidate or delta-update chunks.
- **Reranking and retrieval thresholds** — Cross-encoder or LLM rerank; minimum similarity to reduce irrelevant chunks.
- **Sheets / Slides** — Structured or slide-per-slide extraction pipelines.
- **Streaming responses** — Token streaming for perceived latency (with care for citation consistency).
