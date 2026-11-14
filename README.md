# 🔬 ResearchPilot – AI-Powered Multi-Agent Academic Research Assistant

**ResearchPilot** is an advanced academic research intelligence platform that analyzes uploaded scientific PDFs using a collaborative multi-agent architecture with RAG, a fact-checking critic reflection loop, cross-paper comparison, and contradiction detection.

Unlike generic PDF summarizers or chat interfaces, ResearchPilot performs deep structural academic profiling, maps every retained claim to a retrieved evidence passage with exact page provenance, and enforces a strict evidence-grounding rule.

---

## 🌟 Key Features

### 1. Multi-Agent Collaborative System (6 Autonomous Agents)
- **Agent 1 (Query Agent):** Analyzes the user's research question and decomposes it into 4–8 targeted sub-queries.
- **Agent 2 (Retrieval Agent):** Performs semantic search over the session vector store and standardizes excerpts with unique Evidence IDs (`E001`, `E002`, `E003`...).
- **Agent 3 (Summary Agent):** Synthesizes evidence into thematic academic groupings, attaching Evidence IDs to every factual claim.
- **Agent 4 (Fact-Check Agent / Critic):** Rigorously audits claims against linked passages. Verifies numbers, percentages, and models. Detects exaggerations and flags claims as `Supported`, `Partially Supported`, `Unsupported`, or `Contradicted`. Triggers up to 2 revision loops.
- **Agent 5 (Contradiction Agent):** Detects empirical disagreements across papers, citing Position A and Position B with page numbers, verbatim quotes, and methodological explanations.
- **Agent 6 (Writer Agent):** Enforces strict evidence grounding: keeps ONLY verified claims, dropping ungrounded assertions into an audit log.

### 2. Deep Academic Paper Profiling
- **Section A:** Title, Authors, Publication Year, Abstract, Keywords, Venue, and DOI.
- **Section B:** Research Objectives, Problem Statement, Questions, and Hypotheses.
- **Section C:** Methodology, Experimental Design, Datasets, Sample Sizes, Algorithms, and Evaluation Metrics.
- **Section D:** Major Findings, Numerical Results, Experimental Observations, and Conclusions.
- **Section E:** Author-Acknowledged Limitations, Methodological Weaknesses, and Dataset Constraints.
- **Section F:** Future Directions and Unanswered Questions.

### 3. Cross-Paper Comparison Matrix
- Comparative table across all papers comparing objectives, methodologies, datasets, models, results, and strengths/weaknesses.
- Shared consensus points vs. methodological divergences.

### 4. Interactive Evidence Explorer & Modal Inspector
- Click any claim citation `[E001]` to inspect the exact verbatim text chunk, source paper, and page number.

### 5. Research Gap & Contradiction Detection
- Distinguishes explicitly acknowledged gaps (reported by authors) from AI-inferred potential gaps.
- Compiles actionable future research directions.

### 6. Export Capabilities
- One-click export to formatted academic Markdown (`.md`) or structured JSON (`.json`).

---

## 🏗️ System Architecture

```
User Uploads PDFs & Query
           │
           ▼
PyMuPDF Page Extractor ──► Semantic Chunker ──► ChromaDB (Session-Isolated)
                                                      │
┌─────────────────────────────────────────────────────┴─────────────────────────────────────────────────────┐
│ 1. Query Agent ──► 2. Retrieval Agent (RAG) ──► 3. Summary Agent ──► 4. Fact-Check Critic (Revision Loop) │
│                                                                                     │                     │
│ 6. Writer Agent ◄── Deep Profiler & Gaps ◄── 5. Contradiction Agent ◄───────────────┘                     │
└─────────────────────────────────────────────────────┬─────────────────────────────────────────────────────┘
                                                      ▼
                       ResearchPilot Modern Academic Dashboard (React + Tailwind)
```

---

## 💻 Quickstart Guide (Windows)

### 1. Clone & Install Dependencies

**Backend:**
```powershell
cd "c:\Users\ARCHIT\Desktop\Research Assistant"
pip install -r backend/requirements.txt
```

**Frontend:**
```powershell
cd frontend
npm install
cd ..
```

### 2. Configure Environment

Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
Choose your LLM provider in `.env`:
- **Groq Cloud (Free Tier):** Set `GROQ_API_KEY` with your key.
- **Ollama (100% Local & Private):** Set `LLM_PROVIDER=ollama` and run `ollama pull qwen2.5:1.5b`.

### 3. Start the Application

**Terminal 1 – Start Backend (FastAPI):**
```powershell
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
API Documentation: `http://localhost:8000/docs`

**Terminal 2 – Start Frontend (Vite + React):**
```powershell
cd frontend
npm run dev
```
Open **`http://localhost:5173`** in your browser.

---

## 🧪 Running the Test Suite

Run unit and integration tests for agents, RAG, strict evidence grounding, and session isolation:
```powershell
python -m pytest backend/tests/test_agents_and_rag.py -v
```

---

## ⚖️ Epistemological Disclaimer

This system verifies all claims and conclusions strictly against the uploaded PDF documents, not against universal scientific ground truth. Findings reflect the assertions, datasets, and methodologies of the authors within the provided corpus. No scientific statement is guaranteed to be objectively true merely because it is reported in an uploaded paper.
