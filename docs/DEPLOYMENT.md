# ResearchPilot – Deployment & Configuration Guide

This guide provides instructions to run **ResearchPilot** locally on Windows, configure free model providers (local Ollama or hosted Groq), and deploy publicly.

---

## 1. System Requirements

- **Operating System:** Windows 10/11, macOS, or Linux
- **Python:** 3.10+ (Tested up to Python 3.14)
- **Node.js:** 18+ (Tested on Node v22)
- **RAM:** 8 GB minimum (lightweight embedding model uses ~300 MB)

---

## 2. Windows Local Setup (Step-by-Step)

### Step 1: Install Python Dependencies
Open PowerShell in the project root:
```powershell
cd "c:\Users\ARCHIT\Desktop\Research Assistant"
pip install -r backend/requirements.txt
```

### Step 2: Install Frontend Dependencies
```powershell
cd frontend
npm install
cd ..
```

### Step 3: Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
Open `.env` and configure your preferred LLM provider:

#### Option A: Groq Cloud (Free Tier, Fast)
```env
LLM_PROVIDER=groq
GROQ_API_KEY=your_free_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-20b
```

#### Option B: Ollama (100% Free, Private, Local)
If you want zero cloud dependencies and 100% offline privacy:
1. Download Ollama from [https://ollama.com](https://ollama.com).
2. Pull a lightweight model:
   ```powershell
   ollama pull qwen2.5:1.5b
   ```
3. Set in `.env`:
   ```env
   LLM_PROVIDER=ollama
   OLLAMA_BASE_URL=http://localhost:11434/v1
   OLLAMA_MODEL=qwen2.5:1.5b
   ```

---

## 3. Launching the Application

### Start Backend Server (FastAPI + Uvicorn)
In PowerShell Terminal 1:
```powershell
cd "c:\Users\ARCHIT\Desktop\Research Assistant"
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
Backend API will be live at: `http://localhost:8000` (API docs at `http://localhost:8000/docs`).

### Start Frontend Dev Server (Vite + React)
In PowerShell Terminal 2:
```powershell
cd "c:\Users\ARCHIT\Desktop\Research Assistant\frontend"
npm run dev
```
Open your browser at: **`http://localhost:5173`**.

---

## 4. Running the Automated Test Suite

To run all unit tests for agents, RAG, strict evidence grounding, and session isolation:
```powershell
cd "c:\Users\ARCHIT\Desktop\Research Assistant"
python -m pytest backend/tests/test_agents_and_rag.py -v
```

---

## 5. Free Public Deployment

### Backend (Render or Hugging Face Spaces)
1. **Repository:** Push project to GitHub.
2. **Build Command:** `pip install -r backend/requirements.txt`
3. **Start Command:** `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
4. **Environment Variables:** Add `GROQ_API_KEY` in your service settings dashboard.

### Frontend (Vercel or Netlify)
1. Link your GitHub repository.
2. **Root Directory:** `frontend`
3. **Build Command:** `npm run build`
4. **Output Directory:** `dist`
5. Configure reverse proxy or set `VITE_API_URL` to point to your backend URL.

---

## 6. Model Quota & Privacy Transparency

- **Data Privacy:** Uploaded PDF text chunks are stored in local session-isolated ChromaDB collections and deleted when sessions are reset. If using Groq or OpenAI, text excerpts are transmitted via HTTPS to the provider's API for inference. For zero third-party transmission, use local Ollama.
- **Rate Limit Honesty:** Free tier cloud providers (e.g., Groq free tier) impose daily token quotas. ResearchPilot includes an automatic fallback chain across available open-source models (`openai/gpt-oss-20b`, `qwen/qwen3.8-27b`, etc.) to prevent quota stalls.
