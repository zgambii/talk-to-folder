# Deployment

[← README](../README.md)

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

## Backend (Render)

- **Root directory:** `backend`
- **Build command:** `pip install .`  
  (This repo’s `render.yaml` uses `pip install -e .`; either installs the package from `pyproject.toml`.)
- **Start command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Python:** 3.12+
- Set **`ENVIRONMENT=production`** so session cookies work cross-site with the Vercel frontend (`Secure`, `SameSite=None`).
- Set **`FRONTEND_URL`** to the exact Vercel origin (CORS + cookies).
- Production **`GOOGLE_REDIRECT_URI`** must be the Render callback URL registered in Google Cloud.

## Frontend (Vercel)

- **Root directory:** `frontend`
- Framework preset: **Vite** (usually auto-detected).
- **Environment variable:** `VITE_API_BASE_URL=https://<your-render-service>.onrender.com`

## Supabase in production

Use **`VECTOR_STORE_PROVIDER=supabase`** with the migration applied and secrets set as in [Supabase migration](#supabase-migration) above.
