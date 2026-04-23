# Backend Deployment Guide (Render)

To make your RAG application accessible over the public internet, follow these steps to deploy the FastAPI backend using Render's free tier.

## 1. Prepare Your Repository
Ensure your complete code is pushed to your public GitHub repository.

## 2. Create a Web Service on Render
1. Go to [Render.com](https://render.com/) and log in.
2. Click **New +** and select **Web Service**.
3. Connect your GitHub account and select your repository.

## 3. Configure the Service
Fill out the configuration page as follows:
- **Name**: `dialog-rag-backend` (or similar)
- **Language**: `Docker`
- **Root Directory**: `backend`
- **Instance Type**: Free

*Note: Since we set the language to Docker and the root directory to `backend`, Render will automatically use `backend/Dockerfile` to build and deploy your app.*

## 4. Set Environment Variables
Scroll down to the **Environment Variables** section and add the following keys:
- `LLM_PROVIDER`: `gemini`
- `GEMINI_API_KEY`: Paste your Gemini API key here (DO NOT commit this key to GitHub).
- `CORS_ALLOW_ORIGINS`: `*` (This allows your GitHub pages frontend to access the API. You can change this to your exact GitHub Pages URL later for better security).

## 5. Deploy and Get Your URL
1. Click **Create Web Service**.
2. Wait for the build and deployment to finish (this can take a few minutes on the free tier).
3. Once the deployment is "Live", copy your public URL located near the top left of the dashboard (e.g., `https://dialog-rag-backend-xxxx.onrender.com`).

## 6. Update the Frontend
Now that your backend is deployed, you need to tell your frontend where it is.
1. In your GitHub repository, you can update `frontend/.env` (if using locally) with:
   `VITE_API_BASE_URL=https://<your-render-backend-url>.onrender.com`
2. **For GitHub Pages**: If you want the hosted frontend to use your Render backend, simply add the Render URL to your repository's secrets/variables or temporarily hardcode the `apiBaseDefault` in `frontend/src/App.tsx` before pushing!
