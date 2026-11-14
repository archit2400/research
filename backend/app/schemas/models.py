"""Pydantic schemas and data models for ResearchPilot."""
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EvidencePassage(BaseModel):
    """Retrieved passage from an uploaded paper with unique evidence ID."""
    evidence_id: str = Field(description="Unique identifier, e.g. E001, E002")
    paper_name: str = Field(description="Original PDF filename or title")
    page_number: int = Field(description="1-based page number where passage appears")
    text: str = Field(description="Verbatim excerpt from the paper")
    relevance_score: float = Field(default=0.0, description="Similarity or relevance score")


class Claim(BaseModel):
    """An individual academic claim with attached evidence IDs."""
    claim_id: str = Field(description="Unique claim ID, e.g. C01, C02")
    claim: str = Field(description="The scientific or analytical assertion")
    evidence_ids: List[str] = Field(default_factory=list, description="List of linked EvidencePassage IDs")
    cited_papers: List[str] = Field(default_factory=list, description="Paper titles or filenames cited")
    cited_pages: List[int] = Field(default_factory=list, description="Page numbers cited")
    statement_type: str = Field(default="explicitly_stated", description="'explicitly_stated' or 'ai_inferred'")
    verification_status: Optional[str] = Field(default=None, description="Status after fact-checking")
    critic_reasoning: Optional[str] = Field(default=None, description="Reasoning from the Fact-Check Agent")
    evidence_quotes: List[str] = Field(default_factory=list, description="Verbatim quotes from supporting passages")


class LiteratureTheme(BaseModel):
    """Thematic group of claims in the literature review."""
    theme: str = Field(description="Descriptive academic theme heading")
    claims: List[Claim] = Field(default_factory=list, description="Verified claims in this theme")


class LiteratureReview(BaseModel):
    """Structured thematic literature review."""
    themes: List[LiteratureTheme] = Field(default_factory=list)


class FactCheckStatus(str, Enum):
    SUPPORTED = "Supported"
    PARTIALLY_SUPPORTED = "Partially Supported"
    UNSUPPORTED = "Unsupported"
    CONTRADICTED = "Contradicted"


class FactCheckItem(BaseModel):
    """Fact check critic verification report for an individual claim."""
    claim_id: str
    claim: str
    status: str = Field(default=FactCheckStatus.SUPPORTED.value)
    linked_evidence_ids: List[str] = Field(default_factory=list)
    reason: str = Field(description="Detailed explanation of verification decision")
    numbers_verified: List[str] = Field(default_factory=list, description="Quantitative values checked")
    is_exaggerated: bool = Field(default=False, description="Whether claim overstates findings")
    revision_needed: bool = Field(default=False)
    suggested_revision: Optional[str] = Field(default=None)


class ContradictionItem(BaseModel):
    """Conflicting findings between two or more uploaded papers."""
    topic: str = Field(description="The disputed concept, metric, or outcome")
    position_a: str = Field(description="Assertion or finding in Paper A")
    source_a_paper: str = Field(description="Filename or title of Paper A")
    source_a_page: int = Field(default=1, description="Page number in Paper A")
    source_a_quote: str = Field(default="", description="Verbatim quote from Paper A")
    position_b: str = Field(description="Conflicting assertion or finding in Paper B")
    source_b_paper: str = Field(description="Filename or title of Paper B")
    source_b_page: int = Field(default=1, description="Page number in Paper B")
    source_b_quote: str = Field(default="", description="Verbatim quote from Paper B")
    explanation_of_divergence: str = Field(description="Methodological, dataset, or environmental causes for disagreement")


class ResearchGapItem(BaseModel):
    """Identified research gap distinguishing explicit vs AI-inferred."""
    topic: str = Field(description="Domain or subject of the gap")
    description: str = Field(description="What remains unresolved or unaddressed")
    gap_type: str = Field(description="'explicitly_acknowledged' or 'ai_inferred'")
    source_papers: List[str] = Field(default_factory=list, description="Papers where gap was stated or inferred")
    supporting_evidence_ids: List[str] = Field(default_factory=list)


class ResearchGapAnalysis(BaseModel):
    """Full research gap detection synthesis."""
    under_explored_topics: List[str] = Field(default_factory=list)
    unanswered_research_questions: List[str] = Field(default_factory=list)
    common_limitations_across_studies: List[str] = Field(default_factory=list)
    explicitly_acknowledged_gaps: List[ResearchGapItem] = Field(default_factory=list)
    ai_inferred_gaps: List[ResearchGapItem] = Field(default_factory=list)
    future_research_directions: List[str] = Field(default_factory=list)


class PaperMetadata(BaseModel):
    title: str = Field(default="Not found in paper")
    authors: List[str] = Field(default_factory=lambda: ["Not found in paper"])
    publication_year: str = Field(default="Not found in paper")
    abstract: str = Field(default="Not found in paper")
    keywords: List[str] = Field(default_factory=list)
    venue: str = Field(default="Not found in paper")
    doi: str = Field(default="Not found in paper")


class PaperObjectives(BaseModel):
    main_problem: str = Field(default="Not found in paper")
    objectives: List[str] = Field(default_factory=list)
    research_questions: List[str] = Field(default_factory=list)
    hypotheses: List[str] = Field(default_factory=list)


class PaperMethodology(BaseModel):
    methodology: str = Field(default="Not found in paper")
    experimental_design: str = Field(default="Not found in paper")
    datasets_used: List[str] = Field(default_factory=list)
    sample_size: str = Field(default="Not found in paper")
    algorithms_and_models: List[str] = Field(default_factory=list)
    tools_and_technologies: List[str] = Field(default_factory=list)
    evaluation_metrics: List[str] = Field(default_factory=list)


class PaperResults(BaseModel):
    major_findings: List[str] = Field(default_factory=list)
    numerical_results: List[str] = Field(default_factory=list)
    experimental_observations: List[str] = Field(default_factory=list)
    authors_conclusions: str = Field(default="Not found in paper")


class PaperLimitations(BaseModel):
    author_acknowledged: List[str] = Field(default_factory=list)
    methodological_weaknesses: List[str] = Field(default_factory=list)
    dataset_limitations: List[str] = Field(default_factory=list)
    generalisability_concerns: List[str] = Field(default_factory=list)


class PaperFutureWork(BaseModel):
    future_directions: List[str] = Field(default_factory=list)
    potential_improvements: List[str] = Field(default_factory=list)
    unanswered_questions: List[str] = Field(default_factory=list)


class IndividualPaperAnalysis(BaseModel):
    paper_id: str
    filename: str
    metadata: PaperMetadata
    objectives: PaperObjectives
    methodology: PaperMethodology
    results: PaperResults
    limitations: PaperLimitations
    future_work: PaperFutureWork


class CrossPaperRow(BaseModel):
    paper_title: str
    objectives: str
    methodologies: str
    datasets_and_settings: str
    models_and_techniques: str
    results_and_conclusions: str
    strengths_and_weaknesses: str


class CrossPaperComparison(BaseModel):
    matrix: List[CrossPaperRow] = Field(default_factory=list)
    common_findings: List[str] = Field(default_factory=list)
    different_approaches: List[str] = Field(default_factory=list)
    areas_of_agreement: List[str] = Field(default_factory=list)
    areas_of_disagreement: List[str] = Field(default_factory=list)
    comparative_summary: str = Field(default="")


class DroppedClaim(BaseModel):
    claim_id: str
    claim: str
    status: str
    reason: str
    discrepancies: List[str] = Field(default_factory=list)


class ResearchPipelineResult(BaseModel):
    session_id: str
    question: str
    disclaimer: str
    sub_queries: List[str]
    literature_review: LiteratureReview
    verified_claims: List[Claim]
    dropped_claims: List[DroppedClaim]
    contradiction_analysis: List[ContradictionItem]
    research_gaps: ResearchGapAnalysis
    individual_paper_analyses: List[IndividualPaperAnalysis]
    cross_paper_comparison: CrossPaperComparison
    sources_and_evidence: List[EvidencePassage]
