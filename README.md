# 🔬 ResearchPilot: Multi-Agent Academic Research Assistant

**ResearchPilot** is an orchestrated multi-agent academic intelligence system designed to analyze scientific research papers, synthesize evidence-grounded literature reviews, detect cross-paper contradictions, and verify empirical claims.

---

## 1. Agent Roster

The system organizes six autonomous agents, each with dedicated responsibilities, structured inputs, and strict validation outputs:

| Agent | Module | Input | Output | Role & Responsibility |
|---|---|---|---|---|
| **Query Agent** | `query_agent.py` | Research Question | `List[str]` (4–8 sub-queries) | Decomposes high-level questions into focused sub-queries covering mechanisms, metrics, economic barriers, and topology limits. |
| **Retrieval Agent** | `retrieval_agent.py` | Sub-queries | `List[EvidencePassage]` | Executes multi-query cosine search, deduplicates chunks, and assigns persistent Evidence IDs (`E001`, `E002`...) with page numbers. |
| **Summary Agent** | `summary_agent.py` | Evidence Passages | `LiteratureReview` (Themes & Claims) | Synthesizes findings into thematic clusters, attaching exact `evidence_ids` to every single factual assertion. Handles revision requests from Agent 4. |
| **Fact-Check Critic** | `fact_check_agent.py` | Candidate Claims + Passages | `List[FactCheckItem]` | Audits claims. Statuses: `Supported`, `Partially Supported`, `Unsupported`, `Contradicted`. Checks numbers, detects exaggerations, and initiates reflection loop. |
| **Contradiction Agent** | `contradiction_agent.py` | Passages from 2+ papers | `List[ContradictionItem]` | Identifies conflicting empirical results between papers. Cites Position A and Position B with page numbers, verbatim quotes, and divergence factors. |
| **Writer Agent** | `writer_agent.py` | Audited claims & critic reports | Verified Review + Dropped Claims | **Strict Grounding:** Retains ONLY claims verified as `Supported` with valid `evidence_ids`. Permanently logs dropped claims with rejection reasons. |

---

## 2. Architecture and Why It Fits

```
User Query + Uploaded PDFs
          │
          ▼
   PyMuPDF Ingestion ──► Sliding Chunker ──► ChromaDB (Session-Isolated)
                                                   │
┌──────────────────────────────────────────────────┴──────────────────────────────────────────────────┐
│ Agent 1: Query Agent ──► Agent 2: Retrieval Agent (RAG) ──► Agent 3: Summary Agent                  │
│                                                                      │                              │
│ Agent 6: Writer Agent ◄── Gaps & Profiler ◄── Agent 5: Contradiction Agent ◄── Agent 4: Fact-Check Critic │
│                                                                        (Reflection Loop: Max 2x)    │
└──────────────────────────────────────────────────┬──────────────────────────────────────────────────┘
                                                   ▼
                         Modern Academic Web Dashboard (React + Tailwind)
```

### Why This Architecture Fits Academic Research:
1. **Separation of Generation and Critique:** Single-shot LLMs suffer from cognitive confirmation bias—they believe their own hallucinations. Decoupling the **Summary Agent** (synthesis) from the **Fact-Check Agent** (critic) allows adversarial verification of numbers, percentages, and statements.
2. **Deterministic Revision Loop:** When the critic flags partially supported assertions, it does not abort; it feeds targeted correction constraints back to the Summary Agent (up to 2 iterations), mirroring peer review.
3. **Strict Evidence Provenance:** No claim can enter the final report without an attached `evidence_id` tracing back to an exact page in an uploaded PDF.

---

## 3. Tools per Agent

| Agent | Primary Tools & Capabilities |
|---|---|
| **Query Agent** | LLM Structured JSON Mode, Semantic query decomposition prompt, Deduplication heuristics. |
| **Retrieval Agent** | ChromaDB Collection Query API, Cosine distance calculation, Text normalization, Evidence ID assigner. |
| **Summary Agent** | Thematic Clustering Engine, Citation mapper, Revision-prompt transformer, JSON extraction parser. |
| **Fact-Check Critic** | Regex quantitative number extractor, Exaggeration detection heuristics, Adversarial critic prompt. |
| **Contradiction Agent** | Cross-paper comparator, Methodological divergence analyzer, Verbatim quote extractor. |
| **Writer Agent** | Strict Pydantic evidence filter, Dropped-claims logger, Markdown report compiler. |

---

## 4. What the Memory & Retrieval Holds

ResearchPilot uses **ChromaDB** with **SentenceTransformers** (`all-MiniLM-L6-v2`) for dense semantic retrieval:

- **Session Isolation:** Each research session generates a private vector collection (`session_{session_id}`). Documents uploaded in Session A are physically isolated and can never leak into Session B.
- **Granular Chunk Storage:** Extracted with PyMuPDF preserving 1-based page numbers. Chunks are stored with metadata:
  ```json
  {
    "chunk_id": "paper1_microgrid_p1_c0",
    "paper_id": "paper1_microgrid",
    "paper_name": "paper1_microgrid_storage_resilience.pdf",
    "page_number": 1,
    "text": "verbatim text excerpt...",
    "evidence_id": "E001",
    "relevance_score": 0.94
  }
  ```

---

## 5. One Honest Failure Handled

### Failure: LLM Number Hallucination and Exaggeration
- **Incident:** During initial synthesis of Paper 1, the LLM generated: *"Solar microgrid adoption completely eliminates 100% of household monthly electric utility bills."*
- **Source Truth:** Paper 1 actually states: *"Annual electricity expenditure was reduced by an average of $1,240 per household, with a 42.0% decrease in peak grid dependency."*
- **How It Was Handled:**
  1. **Detection:** The **Fact-Check Critic (`fact_check_agent.py`)** extracts all quantitative values. It checked for `100%` and found zero occurrences in `E001`. It assigned status `Unsupported / Exaggerated` and generated a suggested correction.
  2. **Reflection Loop:** The pipeline triggered the revision loop, prompting the Summary Agent with the critic's exact discrepancy notice.
  3. **Resolution:** The Summary Agent re-grounded the claim to: *"Participating microgrid households saved an average of $1,240 annually with 42.0% peak demand reduction."* The critic re-audited and approved the revision in Pass 2.
  4. **Fallback:** Had the claim remained unsupported, the **Writer Agent** automatically dropped it into the rejected claims log (`dropped_claims`), preventing it from reaching the final literature review.

---

## 6. Quick Start & Verification

```powershell
# 1. Run automated test suite (all 4 scenario tests pass)
python -m pytest backend/tests/test_scenarios.py -v

# 2. Run multi-agent trace demo notebook
jupyter notebook demo_trace.ipynb

# 3. Start Web Application (FastAPI + React Dashboard)
.\start.bat
```
- Web Dashboard: **http://localhost:5173**
- Backend Swagger: **http://localhost:8000/docs**
- Append-Only Run Log: **`logs/run_log.jsonl`**
