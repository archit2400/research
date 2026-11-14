"""Comprehensive tests for ResearchPilot agents, RAG, strict evidence grounding, and session isolation."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from backend.app.agents.contradiction_agent import ContradictionAgent
from backend.app.agents.fact_check_agent import FactCheckAgent
from backend.app.agents.query_agent import QueryAgent
from backend.app.agents.retrieval_agent import RetrievalAgent
from backend.app.agents.summary_agent import SummaryAgent
from backend.app.agents.writer_agent import WriterAgent
from backend.app.ingestion.chunker import DocumentChunker
from backend.app.ingestion.pdf_parser import PDFParser
from backend.app.rag.vector_store import SessionVectorStore
from backend.app.schemas.models import (
    Claim,
    ContradictionItem,
    EvidencePassage,
    FactCheckItem,
    FactCheckStatus,
    LiteratureReview,
    LiteratureTheme,
    ResearchGapAnalysis,
)

SAMPLE_PDF_1 = Path("sample_papers/paper1_microgrid_storage_resilience.pdf")
SAMPLE_PDF_2 = Path("sample_papers/paper2_economic_governance_limits.pdf")
SAMPLE_PDF_3 = Path("sample_papers/paper3_urban_rural_grid_interconnection.pdf")

@pytest.fixture(scope="module")
def sample_test_pdf(tmp_path_factory):
    """Fixture that uses sample_papers/ if present, or creates a temporary multi-page PDF on the fly."""
    if SAMPLE_PDF_1.exists():
        return SAMPLE_PDF_1
    
    import pymupdf
    temp_dir = tmp_path_factory.mktemp("test_pdfs")
    pdf_path = temp_dir / "test_paper_resilience.pdf"
    doc = pymupdf.open()
    
    page1 = doc.new_page(width=595, height=842)
    page1.insert_text((50, 80), "Title: Solar Microgrids and Battery Energy Storage\nAuthors: Dr. Vance\nABSTRACT: Achieved a 94.2% power reliability index during grid outages.", fontsize=11)
    
    page2 = doc.new_page(width=595, height=842)
    page2.insert_text((50, 80), "Page 2 findings: 42.0% decrease in centralized grid dependency.", fontsize=11)
    
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path

# -----------------------------------------------------------------------------
# 1. Ingestion & PDF Extraction Tests
# -----------------------------------------------------------------------------
def test_pdf_extraction_and_page_preservation(sample_test_pdf):
    """Verify PyMuPDF extracts text and accurately preserves page numbers."""
    paper_data = PDFParser.extract_paper(sample_test_pdf)

    assert paper_data["total_pages"] >= 2
    assert len(paper_data["pages"]) == paper_data["total_pages"]
    assert paper_data["pages"][0]["page_number"] == 1
    assert paper_data["pages"][1]["page_number"] == 2
    assert "94.2%" in paper_data["pages"][0]["text"] or "94.2%" in paper_data["pages"][1]["text"]
    assert not paper_data["is_scanned"]


def test_chunking_with_metadata_preservation(sample_test_pdf):
    """Verify text chunker maintains paper name, page number, and chunk IDs."""
    paper_data = PDFParser.extract_paper(sample_test_pdf)
    chunker = DocumentChunker(chunk_size=400, overlap=50)
    chunks = chunker.chunk_paper(paper_data)

    assert len(chunks) > 0
    first_chunk = chunks[0]
    assert "chunk_id" in first_chunk
    assert "paper_id" in first_chunk
    assert "page_number" in first_chunk
    assert first_chunk["page_number"] in [1, 2]
    assert len(first_chunk["text"]) <= 450


# -----------------------------------------------------------------------------
# 2. Vector DB & Session Isolation Tests
# -----------------------------------------------------------------------------
def test_session_isolation_in_vector_store():
    """Ensure user session A cannot retrieve documents indexed in user session B."""
    store_a = SessionVectorStore(session_id="test_session_user_A")
    store_b = SessionVectorStore(session_id="test_session_user_B")

    # Add chunk only to Session A
    chunks_a = [{
        "chunk_id": "test_chunk_a_p1_c0",
        "paper_id": "paper_A",
        "paper_name": "Paper A.pdf",
        "page_number": 1,
        "text": "Unique cryptographic secret alpha-9872 only in User A papers."
    }]
    store_a.add_chunks(chunks_a)

    # Search for this secret in Session B
    results_b = store_b.search(query="cryptographic secret alpha-9872", top_k=5)
    matching_in_b = [r for r in results_b if "alpha-9872" in r["text"]]
    assert len(matching_in_b) == 0, "Session isolation breached: Session B accessed Session A document!"

    # Clean up test collections
    store_a.clear()
    store_b.clear()


# -----------------------------------------------------------------------------
# 3. Agent Unit Tests (Mocked LLM)
# -----------------------------------------------------------------------------
def test_query_agent_generates_subqueries():
    qa = QueryAgent()
    with patch.object(qa.llm, "complete_json", return_value={
        "sub_queries": [
            "What is household power downtime reduction from microgrids?",
            "How do battery storage systems shave peak utility demand?",
            "What are the economic costs per kilowatt for community solar?"
        ]
    }):
        queries = qa.run("How do solar microgrids impact resilience?")
        assert len(queries) >= 3
        assert any("microgrid" in q.lower() for q in queries)


def test_fact_check_agent_detects_unsupported_and_numbers():
    fca = FactCheckAgent()
    passages = [
        EvidencePassage(
            evidence_id="E001",
            paper_name="paper1.pdf",
            page_number=1,
            text="The microgrid achieved a 94.2% power reliability index during storm events.",
            relevance_score=0.95,
        )
    ]

    # Supported claim
    claim_supported = Claim(
        claim_id="C01",
        claim="Microgrids achieved 94.2% power reliability during outages.",
        evidence_ids=["E001"],
    )

    # Unsupported claim (invented metric not in passage)
    claim_unsupported = Claim(
        claim_id="C02",
        claim="Microgrids reduced household water consumption by 88.0%.",
        evidence_ids=["E001"],
    )

    eid_map = {p.evidence_id: p for p in passages}
    res_supported = fca._verify_single_claim_heuristic(claim_supported, eid_map)
    assert res_supported.status == FactCheckStatus.SUPPORTED.value

    res_unsupported = fca._verify_single_claim_heuristic(claim_unsupported, eid_map)
    assert res_unsupported.status in (FactCheckStatus.UNSUPPORTED.value, FactCheckStatus.PARTIALLY_SUPPORTED.value)


def test_fact_check_agent_rejects_claims_without_evidence_ids():
    """STRICT EVIDENCE VALIDATION: Claim without valid evidence ID must be rejected."""
    fca = FactCheckAgent()
    passages = [
        EvidencePassage(
            evidence_id="E001",
            paper_name="paper1.pdf",
            page_number=1,
            text="Real passage text.",
        )
    ]
    # Claim with fabricated ID
    fabricated_claim = Claim(
        claim_id="C99",
        claim="Fabricated claim without real evidence.",
        evidence_ids=["E999_FABRICATED"],
    )
    eid_map = {p.evidence_id: p for p in passages}
    res = fca._verify_single_claim_heuristic(fabricated_claim, eid_map)
    assert res.status == FactCheckStatus.UNSUPPORTED.value
    assert "lacks valid linked evidence" in res.reason.lower()


def test_writer_agent_strictly_excludes_unsupported_claims():
    """Writer Agent must drop unsupported claims and retain only verified claims."""
    wa = WriterAgent()

    review = LiteratureReview(
        themes=[
            LiteratureTheme(
                theme="Resilience",
                claims=[
                    Claim(claim_id="C01", claim="Supported Claim", evidence_ids=["E001"]),
                    Claim(claim_id="C02", claim="Unsupported Claim", evidence_ids=["E001"]),
                ]
            )
        ]
    )

    fact_checks = [
        FactCheckItem(
            claim_id="C01",
            claim="Supported Claim",
            status=FactCheckStatus.SUPPORTED.value,
            reason="Direct support in E001",
        ),
        FactCheckItem(
            claim_id="C02",
            claim="Unsupported Claim",
            status=FactCheckStatus.UNSUPPORTED.value,
            reason="No empirical support in paper",
        ),
    ]

    final_rev, verified, dropped = wa.run(
        original_review=review,
        fact_checks=fact_checks,
        contradictions=[],
        gaps=ResearchGapAnalysis(),
    )

    # Verify C01 kept, C02 dropped
    assert len(verified) == 1
    assert verified[0].claim_id == "C01"
    assert len(dropped) == 1
    assert dropped[0].claim_id == "C02"
    assert len(final_rev.themes[0].claims) == 1


def test_contradiction_agent_identifies_opposing_findings():
    ca = ContradictionAgent()
    passages = [
        EvidencePassage(
            evidence_id="E001",
            paper_name="paper1_microgrid.pdf",
            page_number=1,
            text="Distributed battery storage lowered local distribution line stress by 18.5%.",
        ),
        EvidencePassage(
            evidence_id="E002",
            paper_name="paper3_interconnection.pdf",
            page_number=1,
            text="Uncoordinated battery storage charging cycles exacerbate evening peak ramp stress by up to 24.5%.",
        ),
    ]

    contradictions = ca._heuristic_contradictions(passages)
    assert len(contradictions) >= 1
    assert "stress" in contradictions[0].topic.lower()
    assert contradictions[0].source_a_paper != contradictions[0].source_b_paper
