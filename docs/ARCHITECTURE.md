# ResearchPilot – System Architecture & Multi-Agent Design

## 1. Multi-Agent Collaborative Architecture

ResearchPilot operates as an orchestrated multi-agent academic intelligence system designed to analyze scientific research papers with strict evidence provenance.

```
                              [ User Research Question + Uploaded PDFs ]
                                                 │
                                                 ▼
                                     [ PyMuPDF Text Extractor ]
                                    (Preserves pages 1..N & text)
                                                 │
                                                 ▼
                                     [ Semantic Text Chunker ]
                                 (Sliding window with 100 char overlap)
                                                 │
                                                 ▼
                               [ ChromaDB Vector Store (Session-Isolated) ]
                               (SentenceTransformers: all-MiniLM-L6-v2)
                                                 │
                                                 ▼
                      ┌─────────────────────────────────────────────────────┐
                      │ Agent 1: Query Agent                                │
                      │ - Decomposes topic into 4-8 targeted sub-queries    │
                      └──────────────────────────┬──────────────────────────┘
                                                 │
                                                 ▼
                      ┌─────────────────────────────────────────────────────┐
                      │ Agent 2: Retrieval Agent (RAG)                      │
                      │ - Multi-query cosine search                         │
                      │ - Assigns standardized Evidence IDs (E001, E002...) │
                      └──────────────────────────┬──────────────────────────┘
                                                 │
                                                 ▼
                      ┌─────────────────────────────────────────────────────┐
                      │ Agent 3: Summary Agent                              │
                      │ - Synthesizes findings into academic themes         │
                      │ - Attaches Evidence IDs to every factual claim      │
                      └──────────────────────────┬──────────────────────────┘
                                                 │
                                                 ▼
                      ┌─────────────────────────────────────────────────────┐
                      │ Agent 4: Fact-Check Agent (Critic)                  │
                      │ - Audits numerical values, percentages, & models    │
                      │ - Detects exaggerations and flags status            │
                      └──────────────────────────┬──────────────────────────┘
                                                 │
                            ┌────────────────────┴────────────────────┐
                            │ Status check: Any partially supported?  │
                            └────────────────────┬────────────────────┘
                                     Yes         │         No
                       ┌─────────────────────────┴──┐      │
                       │ Revision Loop (Max 2x)     │      │
                       │ Feedback sent to Agent 3   │      │
                       └────────────────────────────┘      │
                                                 ┌─────────┘
                                                 │
                                                 ▼
                      ┌─────────────────────────────────────────────────────┐
                      │ Agent 5: Contradiction Agent                        │
                      │ - Detects conflicting cross-paper findings          │
                      │ - Extracts Position A vs Position B with quotes     │
                      │ - Explains methodological / feeder divergence       │
                      └──────────────────────────┬──────────────────────────┘
                                                 │
                                                 ▼
                      ┌─────────────────────────────────────────────────────┐
                      │ Deep Paper Profiler & Cross-Paper Matrix Services   │
                      │ - 6-dimensional structural analysis per paper       │
                      │ - Explicit vs AI-inferred research gap detection    │
                      └──────────────────────────┬──────────────────────────┘
                                                 │
                                                 ▼
                      ┌─────────────────────────────────────────────────────┐
                      │ Agent 6: Writer Agent                               │
                      │ - Strict Evidence Grounding Rule enforcement        │
                      │ - Drops any ungrounded assertions into audit log    │
                      │ - Formats themed report with citations & explorer   │
                      └──────────────────────────┬──────────────────────────┘
                                                 │
                                                 ▼
                           [ ResearchPilot Interactive Academic UI ]
```

---

## 2. The Six Autonomous Agents

### Agent 1: Query Agent (`backend/app/agents/query_agent.py`)
- **Input:** Raw research question string.
- **Output:** 4 to 8 targeted, non-overlapping search sub-queries.
- **Role:** Ensures the retrieval stage explores theoretical architectures, empirical findings, quantitative percentages, operational barriers, and limitations.

### Agent 2: Retrieval Agent (`backend/app/agents/retrieval_agent.py`)
- **Input:** Sub-queries from Agent 1.
- **Output:** De-duplicated list of `EvidencePassage` objects.
- **Role:** Executes semantic similarity search against the session-isolated ChromaDB collection. Assigns sequential `evidence_id` tokens (`E001`, `E002`, `E003`...) with relevance scores and page tracking.

### Agent 3: Summary Agent (`backend/app/agents/summary_agent.py`)
- **Input:** Evidence passages and research question.
- **Output:** Structured `LiteratureReview` organized into 2–4 academic themes.
- **Role:** Synthesizes claims across papers while attaching exact `evidence_ids` (`["E001", "E002"]`) to every factual assertion.

### Agent 4: Fact-Check Agent (`backend/app/agents/fact_check_agent.py`)
- **Input:** Candidate claims and linked evidence passages.
- **Output:** List of `FactCheckItem` audit reports.
- **Role:** The Critic. Assigns statuses: `Supported`, `Partially Supported`, `Unsupported`, `Contradicted`. Checks quantitative numbers (percentages, dollar amounts, sample sizes). Triggers revision loop if claims overstate findings.

### Agent 5: Contradiction Agent (`backend/app/agents/contradiction_agent.py`)
- **Input:** Corpus evidence passages from 2 or more distinct papers.
- **Output:** List of `ContradictionItem` objects.
- **Role:** Identifies genuine scientific disagreements. Cites Position A and Position B with exact paper filenames, page numbers, and verbatim quotes. Details why studies diverge (e.g. urban vs rural feeder impedance, coordinated MPC vs uncoordinated battery charging).

### Agent 6: Writer Agent (`backend/app/agents/writer_agent.py`)
- **Input:** Audited claims, fact-checks, contradictions, and gaps.
- **Output:** Final verified literature review, list of verified claims, and list of dropped claims.
- **Strict Evidence Grounding Rule:** Retains ONLY claims verified as `Supported` with at least 1 valid retrieved evidence ID. Unsupported assertions are permanently excluded and logged in the dropped claims audit.

---

## 3. Session Isolation & Epistemology

- **Session Isolation:** Each research session generates a unique isolated ChromaDB collection (`session_<id>`). Papers uploaded in one session are never mixed with another user's session.
- **Epistemological Constraint:** The system verifies assertions against the text of uploaded documents, NOT against universal scientific ground truth. It explicitly avoids declaring a finding scientifically true merely because an author published it.
