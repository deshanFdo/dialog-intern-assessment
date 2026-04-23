# Document Q&A API (RAG)

[![CI](https://github.com/YOUR_USERNAME/dialog-intern-assessment/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/dialog-intern-assessment/actions/workflows/ci.yml)

A Retrieval-Augmented Generation (RAG) application that lets you upload documents and ask questions grounded strictly in the uploaded context. The LLM will answer only from what you provide — if the answer isn't in the text, it replies **"I don't know"**.

## Architecture

```
┌─────────────────┐       ┌──────────────────────────────────┐
│   Frontend       │       │          Backend (FastAPI)        │
│   (Vite + React) │──────▶│                                  │
│                  │       │  POST /ingest  → chunk + index   │
│  • Drag & drop   │       │  POST /ask     → retrieve + LLM  │
│                  │       │  GET  /health  → status check    │
│  Render/Vercel   │       │                                  │
└─────────────────┘       │  RAG: BM25 (rank-bm25)           │
                          │  LLM: Gemini (free tier)         │
                          │                                  │
                          │  Render / Docker                  │
                          └──────────────────────────────────┘
```

## Features

- **Document Ingestion**: Upload text via JSON or `.txt`/`.pdf` file upload
- **Context-Grounded Q&A**: Answers restricted to uploaded content only
- **Conversational Memory (Optional)**: Provide `conversation_id` in `/ask` to remember prior turns
- **Lightweight**: BM25 keyword retrieval — no heavy vector embeddings, fits in 512 MB RAM

## Docs

- Render deployment checklist: `DEPLOY_RENDER.md`
- Assessment requirement mapping: `REQUIREMENTS_COVERAGE.md`

## Repo Structure

```
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── main.py       # API endpoints
│   │   ├── llm.py        # Gemini LLM integration
│   │   └── rag_store.py  # BM25 chunking + retrieval
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/             # Minimal UI (Vite + React)
│   └── src/
│       └── App.tsx
├── .github/workflows/    # CI/CD pipeline
│   └── ci.yml
└── README.md
```

## Quick Start — Docker (Recommended)

### 1) Run the backend

```bash
docker build -t dialog-backend ./backend
docker run --rm -p 8000:8000 \
  -e LLM_PROVIDER=gemini \
  -e GEMINI_API_KEY=your_key_here \
  -e CORS_ALLOW_ORIGINS="http://localhost:5173" \
  dialog-backend
```

### 2) Run the frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

## Quick Start — No Docker

### 1) Backend

```bash
# Create virtual env
python -m venv .venv
source .venv/bin/activate          # Linux/Mac
# .\.venv\Scripts\Activate.ps1    # Windows PowerShell

pip install -r backend/requirements.txt

# Set env vars (pick ONE provider)
export LLM_PROVIDER="gemini"
export GEMINI_API_KEY="your_key_here"
export CORS_ALLOW_ORIGINS="http://localhost:5173"

# Windows PowerShell equivalent:
# $env:LLM_PROVIDER = "gemini"
# $env:GEMINI_API_KEY = "your_key_here"
# $env:CORS_ALLOW_ORIGINS = "http://localhost:5173"

# Run from repo root (recommended):
uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000

# Or run from backend/:
# cd backend
# uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2) Frontend

```bash
cd frontend
npm install
npm run dev
```

## API Reference

### `POST /ingest`

Upload text or a file to build the knowledge base.

**JSON body:**
```json
{ "text": "Paris is the capital of France." }
```

**File upload (multipart):**
```bash
curl -X POST http://localhost:8000/ingest -F "file=@document.pdf"
```

**Response:**
```json
{ "chunks_added": 3, "total_chunks": 3 }
```

### `POST /ask`

Ask a question against the ingested context.

```json
{ "question": "What is the capital of France?" }
```

To enable conversational memory, include `conversation_id`:

```json
{ "question": "What is the capital of France?", "conversation_id": "demo" }
```

**Response:**
```json
{
  "answer": "Paris is the capital of France.",
  "sources": [
    { "id": 1, "text": "Paris is the capital of France..." }
  ]
}
```

### `GET /health`

Health check — returns `{"status": "ok"}`.

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `LLM_PROVIDER` | ❌ | `gemini` | LLM provider (this repo documents `gemini`) |
| `GEMINI_API_KEY` | ✅ | — | Your Google Gemini API key |
| `GEMINI_MODEL` | ❌ | `gemini-2.0-flash` | Gemini model to use |
| `CORS_ALLOW_ORIGINS` | ❌ | `http://localhost:5173` | Comma-separated allowed origins |

## Deploy Backend (Render)

### Option A: Python Runtime

1. Push repo to GitHub
2. Render → **New +** → **Web Service** → connect repo
3. Runtime: **Python** | Root Directory: `backend`
4. Build: `pip install -r requirements.txt`
5. Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Set env vars: `LLM_PROVIDER=gemini`, `GEMINI_API_KEY`, `CORS_ALLOW_ORIGINS`

### Option B: Docker

1. Render → **New +** → **Web Service** → connect repo
2. Environment: **Docker** | Root Directory: `backend`
3. Set env vars: `LLM_PROVIDER=gemini`, `GEMINI_API_KEY`, `CORS_ALLOW_ORIGINS`

## Deploy Frontend

You can host the frontend on **Render (Static Site)** or **Vercel**. Render can host both backend + frontend.

### Option A: Render Static Site (recommended)

1. Render → **New +** → **Static Site** → connect repo
2. Root Directory: `frontend`
3. Build Command: `npm install && npm run build`
4. Publish Directory: `dist`
5. Env var: `VITE_API_BASE_URL` = your Render backend URL
6. Deploy

After deployment, update backend `CORS_ALLOW_ORIGINS` to include your frontend URL.

## Deploy Frontend (Vercel)

1. Import repo in Vercel
2. **Root Directory**: `frontend`
3. Set env var: `VITE_API_BASE_URL` = your Render backend URL
4. Deploy

After deployment, update backend `CORS_ALLOW_ORIGINS` to include your Vercel URL.

## CI/CD

GitHub Actions runs on every push/PR to `main`:
- **Backend lint**: Python syntax check
- **Docker build**: Build image + health check
- **Frontend build**: Vite production build

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11+, FastAPI, uvicorn |
| RAG | BM25 (rank-bm25) — lightweight keyword retrieval |
| LLM | Google Gemini (free tier) |
| PDF parsing | pypdf |
| Frontend | Vite, React 18, TypeScript |
| Containerization | Docker (python:3.11-slim) |
| CI/CD | GitHub Actions |
