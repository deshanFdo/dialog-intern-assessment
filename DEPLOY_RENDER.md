# Deploy on Render (Backend + Frontend)

This repo supports deploying **both** the FastAPI backend and the Vite+React frontend on Render.

## Backend (Web Service)

### 1) Create the service

1. Push this repo to GitHub.
2. Render → **New +** → **Web Service**.
3. Connect your GitHub repo.
4. **Root Directory**: `backend`
5. **Runtime**: Python

### 2) Build / Start commands

- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 3) Environment variables

Set these in Render → **Environment**:

- `LLM_PROVIDER=gemini`
- `GEMINI_API_KEY=<your key>`
- `CORS_ALLOW_ORIGINS=<frontend url>`
  - Example (Render static site): `https://dialog-rag-frontend.onrender.com`

### 4) Get the public backend URL

After deploy, Render will give you a URL like:

- `https://dialog-rag-backend.onrender.com`

Use that as the frontend's `VITE_API_BASE_URL`.

## Frontend (Static Site)

### 1) Create the site

1. Render → **New +** → **Static Site**.
2. Connect the same GitHub repo.
3. **Root Directory**: `frontend`

### 2) Build / Publish

- **Build Command**: `npm install && npm run build`
- **Publish Directory**: `dist`

### 3) Environment variable

- `VITE_API_BASE_URL=https://<your-backend>.onrender.com`

### 4) CORS

Update the backend `CORS_ALLOW_ORIGINS` to include the frontend URL.

## Alternative hosting

- Backend on Render + frontend on Vercel works fine too.
- If you use Vercel, set `VITE_API_BASE_URL` in the Vercel project settings.

## Notes

- Render free tier may spin down when idle; first request can be slow.
- Do not commit real API keys. Use Render env vars.
