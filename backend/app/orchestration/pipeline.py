"""Multi-Agent Research Pipeline with RAG, Critic Reflection Loop, and Strict Evidence Grounding."""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from backend.app.agents import (
    ContradictionAgent,
    FactCheckAgent,
    QueryAgent,
    RetrievalAgent,
    SummaryAgent,
    WriterAgent,
)
from backend.app.config import settings
from backend.app.ingestion import DocumentChunker, PDFParser
from backend.app.rag.vector_store import SessionVectorStore
from backend.app.schemas.models import (
    Claim,
    ContradictionItem,
    CrossPaperComparison,
    DroppedClaim,
    EvidencePassage,
    FactCheckStatus,
    IndividualPaperAnalysis,
    LiteratureReview,
    ResearchGapAnalysis,
    ResearchPipelineResult,
)
from backend.app.services import (
    ComparisonService,
    PaperAnalyzerService,
    ResearchGapAnalyzer,
)

ACADEMIC_DISCLAIMER = (
    "Epistemological Disclaimer: This system verifies all claims and conclusions strictly against "
    "the uploaded PDF documents, not against scientific ground truth. Findings reflect the assertions "
    "and methodologies of the authors within the provided corpus. No scientific statement is guaranteed "
    "to be objectively true merely because it is reported in an uploaded paper."
)

class ResearchPipeline:
    """End-to-end multi-agent orchestration pipeline."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.vector_store = SessionVectorStore(session_id)
        self.pdf_parser = PDFParser()
        self.chunker = DocumentChunker(chunk_size=settings.CHUNK_SIZE, overlap=settings.CHUNK_OVERLAP)

        # 6 Dedicated Autonomous Agents
        self.query_agent = QueryAgent()
        self.retrieval_agent = RetrievalAgent(session_id)
        self.summary_agent = SummaryAgent()
        self.fact_check_agent = FactCheckAgent()
        self.contradiction_agent = ContradictionAgent()
        self.writer_agent = WriterAgent()

        # Advanced Analysis Services
        self.paper_analyzer = PaperAnalyzerService()
        self.comparison_service = ComparisonService()
        self.gap_analyzer = ResearchGapAnalyzer()

    def process_and_index_pdfs(
        self,
        pdf_paths: List[Path | str],
        progress_cb: Optional[Callable[[str, int], None]] = None,
    ) -> List[Dict[str, Any]]:
        """Extract and index uploaded PDF documents into the session's vector store."""
        if progress_cb:
            progress_cb("Extracting text and page boundaries using PyMuPDF...", 10)

        all_papers_data = []
        all_chunks = []

        for p_path in pdf_paths:
            paper_data = self.pdf_parser.extract_paper(p_path)
            all_papers_data.append(paper_data)
            chunks = self.chunker.chunk_paper(paper_data)
            all_chunks.extend(chunks)

        if progress_cb:
            progress_cb(f"Indexing {len(all_chunks)} chunks into session vector space...", 20)

        self.vector_store.add_chunks(all_chunks)
        return all_papers_data

    def run(
        self,
        question: str,
        pdf_paths: List[Path | str],
        progress_cb: Optional[Callable[[str, int], None]] = None,
    ) -> ResearchPipelineResult:
        """Execute full multi-agent collaborative workflow."""
        start_time = time.time()

        # Step 1: Ingestion & Vector Indexing
        papers_data = self.process_and_index_pdfs(pdf_paths, progress_cb)

        # Step 2: Query Agent
        if progress_cb:
            progress_cb("Agent 1 (Query Agent): Formulating 4-8 targeted sub-queries...", 30)
        sub_queries = self.query_agent.run(question)

        # Step 3: Retrieval Agent (RAG)
        if progress_cb:
            progress_cb("Agent 2 (Retrieval Agent): Performing semantic retrieval & assigning Evidence IDs...", 40)
        evidence_passages = self.retrieval_agent.run(sub_queries, top_k_per_query=settings.RETRIEVAL_TOP_K)

        # Step 4: Summary Agent (Initial Synthesis)
        if progress_cb:
            progress_cb("Agent 3 (Summary Agent): Generating theme-based literature synthesis...", 50)
        initial_review = self.summary_agent.run(question, evidence_passages)

        # Step 5: Fact-Check Agent Critic & Reflection Loop (Max 2 Revision Attempts)
        current_review = initial_review
        revision_attempts = 0
        max_attempts = settings.MAX_REVISION_ATTEMPTS

        all_claims = [c for theme in current_review.themes for c in theme.claims]
        fact_checks = []

        while revision_attempts <= max_attempts:
            if progress_cb:
                step_pct = 60 + (revision_attempts * 5)
                progress_cb(f"Agent 4 (Fact-Check Critic): Auditing claims (Pass {revision_attempts + 1})...", step_pct)

            fact_checks = self.fact_check_agent.run(all_claims, evidence_passages)
            unsupported_or_partial = [
                fc for fc in fact_checks
                if fc.status in (FactCheckStatus.UNSUPPORTED.value, FactCheckStatus.PARTIALLY_SUPPORTED.value)
            ]

            # If clean or reached max revisions, break out
            if not unsupported_or_partial or revision_attempts >= max_attempts:
                break

            # Build feedback for Summary Agent to revise
            feedback_lines = []
            for item in unsupported_or_partial:
                feedback_lines.append(f"- Claim [{item.claim_id}]: Status={item.status}. Reason: {item.reason}")
                if item.suggested_revision:
                    feedback_lines.append(f"  Suggested Correction: {item.suggested_revision}")
            feedback_str = "\n".join(feedback_lines)

            if progress_cb:
                progress_cb(f"Summary Agent: Revising {len(unsupported_or_partial)} flagged claims based on critic feedback...", 68)

            current_review = self.summary_agent.revise(current_review, feedback_str, evidence_passages)
            all_claims = [c for theme in current_review.themes for c in theme.claims]
            revision_attempts += 1

        # Step 6: Contradiction Agent
        if progress_cb:
            progress_cb("Agent 5 (Contradiction Agent): Detecting cross-paper conflicting findings...", 75)
        contradictions = self.contradiction_agent.run(evidence_passages)

        # Step 7: Deep Individual Paper Analysis & Cross-Paper Matrix & Gaps
        if progress_cb:
            progress_cb("Analyzing individual papers and generating comparison matrix...", 82)
        individual_analyses = [self.paper_analyzer.analyze_paper(p) for p in papers_data]
        cross_comparison = self.comparison_service.compare_papers(individual_analyses)
        research_gaps = self.gap_analyzer.analyze_gaps(individual_analyses)

        # Step 8: Writer Agent (Strict Evidence Grounding Filter)
        if progress_cb:
            progress_cb("Agent 6 (Writer Agent): Assembling verified report & excluding unsupported claims...", 92)
        final_review, verified_claims, dropped_claims = self.writer_agent.run(
            original_review=current_review,
            fact_checks=fact_checks,
            contradictions=contradictions,
            gaps=research_gaps,
        )

        if progress_cb:
            progress_cb("Complete! Final academic research intelligence report ready.", 100)

        return ResearchPipelineResult(
            session_id=self.session_id,
            question=question,
            disclaimer=ACADEMIC_DISCLAIMER,
            sub_queries=sub_queries,
            literature_review=final_review,
            verified_claims=verified_claims,
            dropped_claims=dropped_claims,
            contradiction_analysis=contradictions,
            research_gaps=research_gaps,
            individual_paper_analyses=individual_analyses,
            cross_paper_comparison=cross_comparison,
            sources_and_evidence=evidence_passages,
        )
