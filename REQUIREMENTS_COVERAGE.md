# Requirements Coverage Matrix

This maps the assessment requirements to the implementation in this repo.

## 1) Application Development & LLM Integration

### REST API endpoints (FastAPI)

- **`POST /ingest`** (text payload or `.txt/.pdf`)
  - Implemented in backend/app/main.py
  - Accepts:
    - JSON: `{ "text": "..." }`
    - Multipart file: `.txt` or `.pdf`
  - PDF extraction via `pypdf`

- **`POST /ask`** (question)
  - Implemented in backend/app/main.py
  - Flow:
    1) retrieve relevant chunks from the ingested store
    2) call LLM with strict grounding prompt
    3) return `{ answer, sources }`

- **`GET /health`**
  - Implemented in backend/app/main.py
  - Returns `{ "status": "ok" }`

### Retrieval / storage

- **In-memory retrieval store**
  - Implemented in backend/app/rag_store.py
  - Uses **BM25** (`rank-bm25`) over chunked text
  - Chunks are stored in memory (lightweight; no embeddings)

### LLM constraints (free-tier)

- Implemented in backend/app/llm.py
- Documented provider:
  - **Google Gemini (free tier)** via `GEMINI_API_KEY`

### Prompt constraints (“context-only” + “I don't know”)

- Enforced in backend/app/main.py (system prompt + guardrails)
- Behavior:
  - If retrieval returns no usable context, API returns **exactly** `"I don't know"`.
  - Otherwise, LLM is instructed to answer **only** from provided context.

## 2) Deployment & Containerization

- **Dockerfile**
  - backend/Dockerfile
  - Uses a slim Python base image; installs only backend requirements.

- **Deployment guidance (public internet)**
  - README.md includes Render deployment steps
  - DEPLOY_RENDER.md provides an end-to-end Render checklist

- **Secrets / API keys**
  - Not committed; provided via environment variables
  - Templates:
    - backend/.env.example
    - frontend/.env.example

## 3) Bonus / “Wow” Factors (Optional)

- **Simple frontend UI**
  - frontend/ (Vite + React + TypeScript)
  - Lets you ingest and ask questions via the backend API

- **Conversational memory**
  - Supported via optional `conversation_id` in `POST /ask`

- **CI/CD**
  - GitHub Actions workflow: .github/workflows/ci.yml
  - Builds backend and frontend; builds Docker image and health-checks it

## Mandatory Deliverables (what you still need to provide)

These are *submission artifacts* (not code) you must produce:

1. **Live URL**: Deploy on Render (or another provider) and paste the public URL(s).
2. **GitHub Repo URL**: Push this repo public and update the README badge URL.
3. **Screen recording (≤ 5 mins)**: Demo + code walkthrough + deployment walkthrough.
