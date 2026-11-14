"""Scenario-Based Test Suite for ResearchPilot Multi-Agent System.

Covers at least three required evaluation scenarios:
- Scenario 1: Supported Claims Grounding (Happy Path).
- Scenario 2: Hallucinated, Exaggerated, and Unsupported Claims Rejection.
- Scenario 3: Cross-Paper Empirical Contradiction Detection.
- Scenario 4: Strict Session-Isolated Vector Memory.
"""
from __future__ import annotations

import pytest
from unittest.mock import patch

from backend.app.agents.contradiction_agent import ContradictionAgent
from backend.app.agents.fact_check_agent import FactCheckAgent
from backend.app.agents.query_agent import QueryAgent
from backend.app.agents.retrieval_agent import RetrievalAgent
from backend.app.agents.summary_agent import SummaryAgent
from backend.app.agents.writer_agent import WriterAgent
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

# -----------------------------------------------------------------------------
# SCENARIO 1: Happy Path - Evidence-Grounded Supported Claims
# -----------------------------------------------------------------------------
def test_scenario_1_supported_claims_grounding():
    """Scenario 1: Verified factual claims with exact numbers must be approved by the Fact-Check Agent and retained by the Writer Agent."""
    fca = FactCheckAgent()
    wa = WriterAgent()

    passages = [
        EvidencePassage(
            evidence_id="E001",
            paper_name="paper1_microgrid_storage_resilience.pdf",
            page_number=1,
            text="localized photovoltaic microgrids equipped with 13.5 kWh lithium iron phosphate batteries achieved a 94.2% power reliability index during severe grid outage events, reducing critical household power downtime from an average of 48.6 hours to 2.8 hours. Participating households exhibited a 42.0% decrease in centralized grid dependency.",
            relevance_score=0.96,
        )
    ]
    eid_map = {p.evidence_id: p for p in passages}

    # Accurate candidate claim citing E001 with true numbers
    claim = Claim(
        claim_id="C01",
        claim="Localized solar microgrids achieved a 94.2% power reliability index and reduced outage downtime to 2.8 hours.",
        evidence_ids=["E001"],
        cited_papers=["paper1_microgrid_storage_resilience.pdf"],
        cited_pages=[1],
    )

    # Fact-Check Critic Audit
    fact_check = fca._verify_single_claim_heuristic(claim, eid_map)
    assert fact_check.status == FactCheckStatus.SUPPORTED.value
    assert "94.2%" in fact_check.numbers_verified or "94.2" in fact_check.numbers_verified
    assert not fact_check.is_exaggerated

    # Writer Agent Compilation
    review = LiteratureReview(themes=[LiteratureTheme(theme="Resilience", claims=[claim])])
    final_rev, verified, dropped = wa.run(
        original_review=review,
        fact_checks=[fact_check],
        contradictions=[],
        gaps=ResearchGapAnalysis(),
    )

    assert len(verified) == 1
    assert verified[0].claim_id == "C01"
    assert len(dropped) == 0
    assert len(final_rev.themes[0].claims) == 1


# -----------------------------------------------------------------------------
# SCENARIO 2: Rejection of Hallucinated, Exaggerated, or Ungrounded Claims
# -----------------------------------------------------------------------------
def test_scenario_2_hallucinated_and_unsupported_claims_rejected():
    """Scenario 2: Claims containing fabricated numerical figures, exaggerations, or missing evidence IDs must be rejected and logged into dropped claims."""
    fca = FactCheckAgent()
    wa = WriterAgent()

    passages = [
        EvidencePassage(
            evidence_id="E001",
            paper_name="paper1_microgrid.pdf",
            page_number=1,
            text="The microgrid achieved 94.2% power reliability on critical circuits.",
            relevance_score=0.92,
        )
    ]
    eid_map = {p.evidence_id: p for p in passages}

    # Case A: Fabricated number (claims 99.9% instead of 94.2%)
    claim_hallucinated_num = Claim(
        claim_id="C_FAKE_NUM",
        claim="The microgrid achieved 99.9% power reliability across all systems.",
        evidence_ids=["E001"],
    )
    res_num = fca._verify_single_claim_heuristic(claim_hallucinated_num, eid_map)
    assert res_num.status in (FactCheckStatus.UNSUPPORTED.value, FactCheckStatus.PARTIALLY_SUPPORTED.value)
    assert res_num.is_exaggerated is True

    # Case B: Completely ungrounded claim with fabricated Evidence ID
    claim_fabricated_eid = Claim(
        claim_id="C_FAKE_EID",
        claim="Community solar completely eliminates household municipal water bills.",
        evidence_ids=["E_NONEXISTENT_999"],
    )
    res_eid = fca._verify_single_claim_heuristic(claim_fabricated_eid, eid_map)
    assert res_eid.status == FactCheckStatus.UNSUPPORTED.value

    # Writer Agent must exclude both from final literature review
    review = LiteratureReview(themes=[
        LiteratureTheme(theme="General", claims=[claim_hallucinated_num, claim_fabricated_eid])
    ])
    final_rev, verified, dropped = wa.run(
        original_review=review,
        fact_checks=[res_num, res_eid],
        contradictions=[],
        gaps=ResearchGapAnalysis(),
    )

    assert len(verified) == 0, "No ungrounded claims may appear in verified claims!"
    assert len(dropped) == 2, "Both ungrounded claims must be present in dropped claims log!"
    assert len(final_rev.themes) == 0 or len(final_rev.themes[0].claims) == 0


# -----------------------------------------------------------------------------
# SCENARIO 3: Cross-Paper Contradiction Detection
# -----------------------------------------------------------------------------
def test_scenario_3_cross_paper_contradiction_detection():
    """Scenario 3: Contradiction Agent must identify conflicting findings across papers, presenting both positions and divergence explanations without taking sides."""
    ca = ContradictionAgent()

    passages = [
        EvidencePassage(
            evidence_id="E001",
            paper_name="paper1_microgrid_storage_resilience.pdf",
            page_number=1,
            text="aggregate frequency regulation services from distributed battery storage microgrids lowered local distribution feeder stress by 18.5%.",
            relevance_score=0.94,
        ),
        EvidencePassage(
            evidence_id="E005",
            paper_name="paper3_urban_rural_grid_interconnection.pdf",
            page_number=1,
            text="Contrary to prior claims that residential battery storage inherently resolves rural feeder instability, our findings indicate that uncoordinated storage charging cycles exacerbate evening peak ramp stress by up to 24.5%.",
            relevance_score=0.91,
        ),
    ]

    contradictions = ca._heuristic_contradictions(passages)
    assert len(contradictions) >= 1

    c = contradictions[0]
    assert "stress" in c.topic.lower()
    assert c.source_a_paper != c.source_b_paper
    assert len(c.source_a_quote) > 10
    assert len(c.source_b_quote) > 10
    assert len(c.explanation_of_divergence) > 20


# -----------------------------------------------------------------------------
# SCENARIO 4: Strict Session-Isolated Memory Retrieval
# -----------------------------------------------------------------------------
def test_scenario_4_session_isolation():
    """Scenario 4: Ensures one user session's vector space and uploaded papers can never leak into another user's session."""
    session_alpha = SessionVectorStore(session_id="user_session_alpha_001")
    session_beta = SessionVectorStore(session_id="user_session_beta_002")

    session_alpha.add_chunks([{
        "chunk_id": "alpha_doc_p1_c0",
        "paper_id": "alpha_paper",
        "paper_name": "Confidential_Alpha.pdf",
        "page_number": 1,
        "text": "Proprietary confidential clinical trials batch #ZX-9844."
    }])

    # Search in Session Beta
    beta_results = session_beta.search(query="clinical trials batch #ZX-9844", top_k=5)
    leaked = [r for r in beta_results if "ZX-9844" in r["text"]]
    assert len(leaked) == 0, "Security Violation: Document leaked across session boundaries!"

    session_alpha.clear()
    session_beta.clear()
