# 🔬 ResearchPilot: How It Works & Comprehensive Codebase Guide

This document provides a complete, in-depth architectural explanation of **ResearchPilot – AI-Powered Multi-Agent Academic Research Assistant**. It explains the entire end-to-end workflow, the multi-agent critic collaboration loop, and a detailed file-by-file breakdown of what every file in the project contains and does.

---

## Table of Contents
1. [Core Purpose & Philosophy](#1-core-purpose--philosophy)
2. [End-to-End System Workflow](#2-end-to-end-system-workflow)
3. [The Six-Agent Architecture & Critic Loop](#3-the-six-agent-architecture--critic-loop)
4. [File-by-File Codebase Directory](#4-file-by-file-codebase-directory)
   - [Root Startup Scripts & Config](#root-startup-scripts--config)
   - [Backend Application (`backend/app/`)](#backend-application-backendapp)
     - [FastAPI Main & Config](#fastapi-main--config)
     - [Schemas & Data Models (`backend/app/schemas/`)](#schemas--data-models-backendappschemas)
     - [LLM Provider Layer (`backend/app/llm/`)](#llm-provider-layer-backendappllm)
     - [PDF Ingestion & Chunking (`backend/app/ingestion/`)](#pdf-ingestion--chunking-backendappingestion)
     - [RAG & Vector Storage (`backend/app/rag/`)](#rag--vector-storage-backendapprag)
     - [The 6 Autonomous Agents (`backend/app/agents/`)](#the-6-autonomous-agents-backendappagents)
     - [Deep Analysis Services (`backend/app/services/`)](#deep-analysis-services-backendappservices)
     - [Orchestration Pipeline (`backend/app/orchestration/`)](#orchestration-pipeline-backendapporchestration)
     - [Test Suite (`backend/tests/`)](#test-suite-backendtests)
   - [Frontend React Application (`frontend/`)](#frontend-react-application-frontend)
     - [Core Config & Shell](#core-config--shell)
     - [API Client Service](#api-client-service)
     - [UI Components & Modals](#ui-components--modals)
     - [The 8 Result Tabs](#the-8-result-tabs)
   - [Sample Corpus & Documentation](#sample-corpus--documentation)
5. [Data Flow & Schema Journey](#5-data-flow--schema-journey)
6. [Epistemological Guardrail & Strict Evidence Rule](#6-epistemological-guardrail--strict-evidence-rule)

---

## 1. Core Purpose & Philosophy

Traditional PDF summarizers simply feed raw text into a chatbot prompt and produce high-level summaries prone to hallucinations, fabricated citations, and unverified assertions.

**ResearchPilot** is an academic research platform built on three principles:
1. **Strict Evidence Provenance:** Every retained claim in the literature review must map to an exact retrieved passage (`E001`, `E002`...) with original paper name and page number.
2. **Multi-Agent Critic Reflection:** AI agents do not write unchecked summaries. A dedicated **Fact-Check Critic Agent** audits every claim against source passages, checks quantitative numbers (percentages, dollars, hours), detects exaggerations, and triggers up to two revision cycles before any text is published.
3. **Session-Isolated Vector Collections:** ChromaDB creates a private, isolated vector collection for every research session (`session_<id>`), ensuring that papers uploaded by different users are never commingled.

---

## 2. End-to-End System Workflow

```
[ User Uploads PDFs & Query in Web UI ]
                   │
                   ▼
  1. PDF Ingestion (PyMuPDF)
     - Extracts text page-by-page (preserves page numbers 1..N).
     - Checks for rasterized scanned PDFs.
                   │
                   ▼
  2. Semantic Chunking
     - Recursive sliding window (600 characters with 100 character overlap).
     - Tags each chunk with paper name, title, page number, and chunk index.
                   │
                   ▼
  3. Session-Isolated Vector Indexing (ChromaDB)
     - Embeds chunks using SentenceTransformers ('all-MiniLM-L6-v2').
     - Stored under collection: 'session_{session_id}'.
                   │
                   ▼
  4. Multi-Agent Collaborative Pipeline
     ├─ Agent 1 (Query Agent): Decomposes query into 4-8 sub-queries.
     ├─ Agent 2 (Retrieval Agent): Performs semantic search & assigns IDs (E001, E002...).
     ├─ Agent 3 (Summary Agent): Groups findings into themes & attaches Evidence IDs.
     ├─ Agent 4 (Fact-Check Critic): Audits numbers, checks support, flags exaggerations.
     │      └── Revision Loop: If claims are unsupported, Agent 3 revises (max 2x).
     ├─ Agent 5 (Contradiction Agent): Detects cross-paper conflicts with quotes & reasons.
     ├─ Deep Profiler & Gaps: Extracts 6-part paper profiles & explicit vs AI gaps.
     └─ Agent 6 (Writer Agent): Strict filter. Drops ungrounded claims into rejection log.
                   │
                   ▼
  5. Interactive Results Dashboard (React + Tailwind)
     - 8 Interactive Tabs, KPI strip, and Clickable Evidence Inspector Modal.
     - One-click export to Academic Markdown (.md) or JSON (.json).
```

---

## 3. The Six-Agent Architecture & Critic Loop

Each agent is an independent Python module with structured inputs and outputs:

| Agent | Module File | Primary Input | Primary Output | Responsibility |
|---|---|---|---|---|
| **Agent 1: Query Agent** | `query_agent.py` | Research question string | `List[str]` (4–8 sub-queries) | Breaks down a question into empirical, numerical, governance, and grid-stress angles. |
| **Agent 2: Retrieval Agent** | `retrieval_agent.py` | Sub-queries from Agent 1 | `List[EvidencePassage]` | Searches vector DB, de-duplicates chunks, assigns clean sequential Evidence IDs (`E001`, `E002`...). |
| **Agent 3: Summary Agent** | `summary_agent.py` | Evidence passages | `LiteratureReview` (Themes & Claims) | Synthesizes findings into academic themes, attaching `evidence_ids` to every claim. |
| **Agent 4: Fact-Check Critic** | `fact_check_agent.py` | Candidate claims + passages | `List[FactCheckItem]` | Audits claims. Statuses: `Supported`, `Partially Supported`, `Unsupported`, `Contradicted`. Triggers revision loop if numbers or claims are unverified. |
| **Agent 5: Contradiction Agent** | `contradiction_agent.py` | Passages from 2+ papers | `List[ContradictionItem]` | Identifies conflicting findings (e.g. Paper 1 says storage stabilizes lines; Paper 3 says it exacerbates ramp stress). Explains methodological divergence. |
| **Agent 6: Writer Agent** | `writer_agent.py` | Audited claims & critic reports | Verified Review + Dropped Claims | **Strict Grounding:** Retains ONLY claims verified as `Supported` with valid `evidence_ids`. Permanently logs dropped claims with rejection reasons. |

---

## 4. File-by-File Codebase Directory

### Root Startup Scripts & Config

- **`start.bat`**: Windows batch script. Double-clicking this launches both the FastAPI backend (port 8000) and the Vite frontend (port 5173) in separate command prompt windows.
- **`run.ps1`**: PowerShell equivalent startup script with color-coded status output.
- **`run_backend.py`**: Portable Python runner that automatically adds the project root to `sys.path` and starts Uvicorn. Can be executed from any directory without `ModuleNotFoundError: No module named 'backend'` errors.
- **`.env`**: Local environment variables containing `LLM_PROVIDER`, `GROQ_API_KEY`, `GROQ_MODEL`, `OLLAMA_BASE_URL`, `EMBEDDING_MODEL`, and retrieval settings.
- **`.env.example`**: Safe template with placeholder keys for GitHub version control.
- **`.gitignore`**: Excludes `node_modules/`, `dist/`, `.env`, `chroma_db/`, and Python cache artifacts from Git.
- **`README.md`**: High-level public documentation, system overview, and installation commands.

---

### Backend Application (`backend/app/`)

#### FastAPI Main & Config
- **`backend/app/main.py`**:
  - The entry point for the REST API.
  - Configures CORS middleware for frontend communication (`http://localhost:5173`).
  - Implements session management in `SESSIONS` memory store.
  - Endpoints:
    - `GET /api/health`: Health status, active LLM provider, sample paper counts.
    - `POST /api/upload`: Uploads multiple PDF files into session-isolated folders.
    - `POST /api/load-sample`: Copies benchmark papers into a fresh session for testing.
    - `POST /api/research`: Launches background execution of `ResearchPipeline`.
    - `GET /api/session/{id}/status`: Polls real-time progress percentage (0–100%) and stage messages.
    - `GET /api/session/{id}/report`: Returns full JSON research results.
    - `GET /api/session/{id}/export/markdown`: Downloads formatted academic Markdown.
    - `GET /api/session/{id}/export/json`: Downloads complete raw JSON report.
- **`backend/app/config.py`**:
  - Centralized `Settings` class loading configuration from `.env`.
  - Configures retrieval thresholds, chunk sizes, ChromaDB directory, and upload paths.

#### Schemas & Data Models (`backend/app/schemas/`)
- **`backend/app/schemas/models.py`**:
  - Type-enforced Pydantic v2 schemas:
    - `EvidencePassage`: Standardized passage with `evidence_id` (`E001`...), `paper_name`, `page_number`, `text`, `relevance_score`.
    - `Claim`: A scientific assertion with linked `evidence_ids`, `cited_papers`, `cited_pages`, `statement_type` (*explicitly_stated* vs *ai_inferred*), and `verification_status`.
    - `LiteratureTheme`: Thematic container grouping related claims.
    - `LiteratureReview`: The collection of themes and claims.
    - `FactCheckItem`: Critic audit report containing verification status (`Supported`, `Partially Supported`, `Unsupported`, `Contradicted`), verified numbers list, exaggeration flags, and revision suggestions.
    - `ContradictionItem`: Disagreement pair containing Position A (paper, page, quote), Position B (paper, page, quote), and `explanation_of_divergence`.
    - `ResearchGapItem` & `ResearchGapAnalysis`: Structural gaps categorized into explicitly acknowledged vs. AI-inferred gaps.
    - `IndividualPaperAnalysis`: 6-dimensional paper profile (Metadata, Objectives, Methodology, Results, Limitations, Future Work).
    - `CrossPaperComparison`: Comparative matrix rows and synthesis.
    - `ResearchPipelineResult`: Top-level envelope containing the full analysis payload.
- **`backend/app/schemas/__init__.py`**: Exports all schema classes for clean imports.

#### LLM Provider Layer (`backend/app/llm/`)
- **`backend/app/llm/provider.py`**:
  - Provider-agnostic LLM client supporting **Groq**, **Ollama** (local offline), and **OpenAI**.
  - `complete()`: Dispatches chat completions with temperature and token limits.
  - `complete_json()`: Enforces JSON output, repairs malformed markdown wrappers (````json ... ````), and retries on parse failures.
  - Model fallback chain: Automatically falls back across available models (`openai/gpt-oss-20b`, `qwen/qwen3.8-27b`, `openai/gpt-oss-120b`) if a model encounters rate limits (HTTP 429) or deprecations.
- **`backend/app/llm/__init__.py`**: Exports the global `llm` instance.

#### PDF Ingestion & Chunking (`backend/app/ingestion/`)
- **`backend/app/ingestion/pdf_parser.py`**:
  - Uses PyMuPDF (`pymupdf`) for page-by-page text extraction.
  - Preserves exact 1-based page numbers.
  - Scanned PDF detection: Calculates character density per page; if below 50 characters/page, flags `is_scanned: True` and informs user that OCR is required.
- **`backend/app/ingestion/chunker.py`**:
  - Splits extracted pages into overlapping text chunks (default 600 characters with 100 character overlap).
  - Preserves metadata: `chunk_id`, `paper_id`, `paper_name`, `page_number`, and `text`.
- **`backend/app/ingestion/__init__.py`**: Exports `PDFParser` and `DocumentChunker`.

#### RAG & Vector Storage (`backend/app/rag/`)
- **`backend/app/rag/vector_store.py`**:
  - Manages session-isolated ChromaDB persistent collections (`session_{session_id}`).
  - Uses `SentenceTransformerEmbeddingFunction` with `all-MiniLM-L6-v2`.
  - `add_chunks()`: Upserts text chunks and metadata into the session's vector space.
  - `search()`: Executes cosine similarity search and converts distances to similarity scores.
  - `clear()`: Deletes session collection when research is reset.
- **`backend/app/rag/__init__.py`**: Exports `SessionVectorStore`.

#### The 6 Autonomous Agents (`backend/app/agents/`)
- **`backend/app/agents/query_agent.py`**:
  - **Agent 1:** Prompted to understand the research topic and produce 4–8 diverse sub-queries covering mechanisms, methodologies, quantitative results, barriers, and limitations.
- **`backend/app/agents/retrieval_agent.py`**:
  - **Agent 2:** Executes RAG retrieval over all sub-queries, eliminates duplicates, ranks by relevance, and formats passages into standardized `EvidencePassage` objects with clean sequential IDs (`E001`, `E002`, `E003`...).
- **`backend/app/agents/summary_agent.py`**:
  - **Agent 3:** Thematic literature synthesis. Organizes claims into academic themes, links every claim to valid `evidence_ids`, and handles revision requests from Agent 4.
- **`backend/app/agents/fact_check_agent.py`**:
  - **Agent 4 (Critic):** Audits every claim against linked passage text. Checks numerical values, percentages, and dollar figures. Identifies exaggerations. Contains both LLM verification and deterministic heuristic fallback.
- **`backend/app/agents/contradiction_agent.py`**:
  - **Agent 5:** Compares findings across distinct papers. Identifies conflicting empirical results, extracts verbatim quotes, citations, and explains why studies diverge.
- **`backend/app/agents/writer_agent.py`**:
  - **Agent 6:** The final report compiler. Enforces the strict evidence rule: keeps only `Supported` claims with verified evidence IDs, while routing ungrounded claims into `dropped_claims`.
- **`backend/app/agents/__init__.py`**: Exports all 6 agent classes.

#### Deep Analysis Services (`backend/app/services/`)
- **`backend/app/services/paper_analyzer.py`**:
  - Extracts 6 deep structural sections for each uploaded paper: (A) Metadata, (B) Objectives, (C) Methodology, (D) Results, (E) Limitations, and (F) Future Work.
- **`backend/app/services/comparison_service.py`**:
  - Synthesizes the cross-paper comparative matrix across objectives, methodologies, datasets, models, results, and strengths/weaknesses.
- **`backend/app/services/gap_analyzer.py`**:
  - Distinguishes explicitly acknowledged research gaps from AI-inferred gaps across the corpus.
- **`backend/app/services/markdown_exporter.py`**:
  - Serializes the entire research report into academic Markdown (`.md`) format for export.
- **`backend/app/services/__init__.py`**: Exports all services.

#### Orchestration Pipeline (`backend/app/orchestration/`)
- **`backend/app/orchestration/pipeline.py`**:
  - Orchestrates the full 8-step workflow.
  - Manages the critic reflection loop: if Agent 4 identifies unsupported or partially supported claims, it sends structured feedback back to Agent 3 to revise (up to 2 iterations).
  - Embeds the mandatory `ACADEMIC_DISCLAIMER`.
- **`backend/app/orchestration/__init__.py`**: Exports `ResearchPipeline` and `ACADEMIC_DISCLAIMER`.

#### Test Suite (`backend/tests/`)
- **`backend/tests/test_agents_and_rag.py`**:
  - 8 automated tests:
    1. PDF text extraction & page-number preservation.
    2. Overlapping text chunking & metadata integrity.
    3. Session isolation (verifies Session B cannot access Session A papers).
    4. Query Agent sub-query decomposition.
    5. Fact-Check Agent quantitative number checking.
    6. Strict evidence grounding rule (claims without evidence IDs are rejected).
    7. Writer Agent filtering (unsupported claims excluded).
    8. Contradiction detection across conflicting findings.

---

### Frontend React Application (`frontend/`)

#### Core Config & Shell
- **`frontend/package.json`**: Defines React 18, Vite, Tailwind CSS, and Lucide React icons.
- **`frontend/vite.config.js`**: Vite configuration with reverse proxy routing `/api` requests to `http://localhost:8000`.
- **`frontend/tailwind.config.js`**: Tailwind CSS configuration with dark mode support.
- **`frontend/postcss.config.js`**: PostCSS plugins for Tailwind and Autoprefixer.
- **`frontend/index.html`**: HTML entry point with Inter font styling.
- **`frontend/src/index.css`**: Tailwind directives and custom scrollbar styling.
- **`frontend/src/main.jsx`**: React root mount.
- **`frontend/src/App.jsx`**: The main application controller. Manages session ID, PDF file list, research query, polling status, dark/light theme, active tab state, and the Evidence Modal.

#### API Client Service
- **`frontend/src/services/api.js`**: Asynchronous HTTP client communicating with FastAPI endpoints (`uploadPapers`, `loadSamplePapers`, `startResearch`, `getSessionStatus`, `getReport`, `exportMarkdownUrl`, `exportJsonUrl`).

#### UI Components & Modals
- **`frontend/src/components/Navbar.jsx`**: Top header displaying ResearchPilot logo, active LLM model badge, dark/light mode toggle, and "New Session" reset button.
- **`frontend/src/components/UploadSection.jsx`**: Drag-and-drop PDF upload zone, uploaded paper chip list with remove buttons, and sample benchmark loader.
- **`frontend/src/components/QuestionInput.jsx`**: Clean research question input box and "Launch Academic Intelligence Pipeline" button.
- **`frontend/src/components/ProgressTracker.jsx`**: Real-time progress bar showing the active agent among the 8 pipeline stages.
- **`frontend/src/components/EvidenceModal.jsx`**: Slide-over inspector modal that opens when any `[E001]` citation badge is clicked. Shows exact verbatim text, source paper, page number, relevance percentage, and all claims linked to that passage.

#### The 8 Result Tabs (`frontend/src/components/tabs/`)
1. **`LiteratureReviewTab.jsx`**: Displays themes, claims, clickable `[E001]` evidence pills, statement type tags, and expandable verbatim quotes.
2. **`IndividualPaperTab.jsx`**: Paper selector dropdown displaying deep extracted profiles across all 6 sections (Metadata, Objectives, Methodology, Results, Limitations, Future Work).
3. **`PaperComparisonTab.jsx`**: Cross-paper matrix table, shared findings, and methodological divergences.
4. **`FactCheckerTab.jsx`**: Audit screen with filter buttons (*All*, *Supported*, *Rejected*), critic reasoning notes, and quantitative verification badges.
5. **`ContradictionTab.jsx`**: Side-by-side Position A vs. Position B cards with quotes, page provenance, and divergence explanations.
6. **`ResearchGapsTab.jsx`**: Displays explicitly acknowledged gaps from authors alongside AI-inferred gaps and future directions.
7. **`EvidenceExplorerTab.jsx`**: Searchable repository of all retrieved evidence passages with relevance scores and modal inspection links.
8. **`ExportReportTab.jsx`**: One-click download buttons for Academic Markdown (`.md`) and JSON (`.json`) with KPI summary metrics.

---

### Sample Corpus & Documentation

- **`sample_papers/`**:
  - `paper1_microgrid_storage_resilience.pdf`: Florida coastal microgrid resilience study (N=150, 94.2% reliability, $1,240 savings).
  - `paper2_economic_governance_limits.pdf`: Low-income community solar barriers study (85 projects, 68.2% insolvency, 53.4% credit disqualification).
  - `paper3_urban_rural_grid_interconnection.pdf`: Urban vs. rural feeder interconnection study (80 feeders, 3.4x flicker, reverse power flow on 28% of circuits).
- **`docs/ARCHITECTURE.md`**: Detailed technical architecture and agent specifications.
- **`docs/DEPLOYMENT.md`**: Deployment guide for Windows, Ollama local setup, Docker, and free cloud hosting.

---

## 5. Data Flow & Schema Journey

Here is how data moves through the schemas during execution:

1. **PDF File** on disk is read by `PDFParser` $\rightarrow$ parsed into a Python dictionary containing `pages: [{"page_number": int, "text": str}]`.
2. **Pages** are split by `DocumentChunker` $\rightarrow$ produces chunk dictionaries with `chunk_id: "{paper_id}_p{page}_c{chunk}"`.
3. **Chunks** are embedded by `SessionVectorStore` $\rightarrow$ stored in ChromaDB collection `session_{session_id}`.
4. **Sub-queries** from `QueryAgent` $\rightarrow$ queried by `RetrievalAgent` $\rightarrow$ converted into standardized `EvidencePassage` objects (`evidence_id="E001"`, `paper_name="paper1.pdf"`, `page_number=1`, `text="..."`).
5. **Passages** are synthesized by `SummaryAgent` $\rightarrow$ transformed into `Claim` objects grouped inside `LiteratureTheme` objects.
6. **Claims** are audited by `FactCheckAgent` $\rightarrow$ produces `FactCheckItem` reports with verification status.
7. **WriterAgent** filters claims $\rightarrow$ approved claims go into `verified_claims`; rejected claims go into `dropped_claims`.
8. The entire bundle is serialized into `ResearchPipelineResult` $\rightarrow$ sent as JSON to the React frontend.

---

## 6. Epistemological Guardrail & Strict Evidence Rule

### Strict Evidence Grounding Rule
In `writer_agent.py`:
```python
if fc and fc.status == "Supported" and claim.evidence_ids:
    # Retained in final Literature Review
    approved_theme_claims.append(claim)
    verified_claims.append(claim)
else:
    # Permanently excluded from Literature Review
    dropped_claims.append(DroppedClaim(...))
```
**No claim without a valid retrieved evidence passage ID can ever appear in the final literature review.**

### Academic Epistemology Notice
Embedded in every generated report:
> *"This system verifies claims and conclusions strictly against the uploaded PDF documents, not against scientific ground truth. Findings reflect the assertions, datasets, and methodologies of the authors within the provided corpus. No scientific statement is guaranteed to be objectively true merely because it is reported in an uploaded paper."*
