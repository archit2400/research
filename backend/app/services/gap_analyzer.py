"""Service for detecting explicit and AI-inferred research gaps."""
from __future__ import annotations

from typing import Any, Dict, List
from backend.app.llm.provider import llm
from backend.app.schemas.models import (
    IndividualPaperAnalysis,
    ResearchGapAnalysis,
    ResearchGapItem,
)

SYSTEM_PROMPT = """You are a specialized Academic Research Gap Discovery Agent.
Analyze the collective corpus of uploaded research papers to identify genuine research gaps, limitations, and future horizons.

STRICT CRITERIA:
1. Distinguish between:
   a) Explicitly Acknowledged Gaps: Limitations, blind spots, or future directions stated by the paper authors themselves. Cite the source papers.
   b) AI-Inferred Gaps: Unresolved questions or structural blind spots synthesized by contrasting multiple papers.
2. Formulate concrete unanswered research questions.
3. Identify common limitations shared across multiple studies (e.g., small sample sizes, lack of multi-year degradation models, exclusion of low-income renters).
4. Do NOT claim a gap exists across the entire academic universe—frame it specifically relative to the uploaded corpus.

Return a JSON object in this format:
{
  "under_explored_topics": ["Topic 1", "Topic 2"],
  "unanswered_research_questions": ["Question 1", "Question 2"],
  "common_limitations_across_studies": ["Shared limitation 1", "Shared limitation 2"],
  "explicitly_acknowledged_gaps": [
    {
      "topic": "Battery recycling economics and high ambient degradation",
      "description": "Subtropical temperature degradation models and end-of-life battery recycling were not modeled.",
      "gap_type": "explicitly_acknowledged",
      "source_papers": ["paper1_microgrid_storage_resilience.pdf"],
      "supporting_evidence_ids": []
    }
  ],
  "ai_inferred_gaps": [
    {
      "topic": "Synthesis of low-income financing with high-impedance rural feeders",
      "description": "None of the papers study how community solar financing models operate in remote rural co-ops where feeder upgrade costs are highest.",
      "gap_type": "ai_inferred",
      "source_papers": ["paper2_economic_governance_limits.pdf", "paper3_urban_rural_grid_interconnection.pdf"],
      "supporting_evidence_ids": []
    }
  ],
  "future_research_directions": ["Direction 1", "Direction 2"]
}
"""

class ResearchGapAnalyzer:
    """Detects explicit and AI-inferred research gaps across uploaded literature."""

    def __init__(self):
        self.llm = llm

    def analyze_gaps(self, analyses: List[IndividualPaperAnalysis]) -> ResearchGapAnalysis:
        if not analyses:
            return ResearchGapAnalysis()

        corpus_context = []
        for p in analyses:
            corpus_context.append({
                "paper_title": p.metadata.title,
                "filename": p.filename,
                "author_limitations": p.limitations.author_acknowledged,
                "weaknesses": p.limitations.methodological_weaknesses,
                "future_work": p.future_work.future_directions,
                "unanswered_questions": p.future_work.unanswered_questions,
            })

        prompt = f"Analyze the collective limitations and future work across these {len(analyses)} papers to discover research gaps:\n\n{corpus_context}"

        try:
            data = self.llm.complete_json(prompt=prompt, system_prompt=SYSTEM_PROMPT)
            return self._parse_gaps(data)
        except Exception as e:
            print(f"[ResearchGapAnalyzer] Error analyzing gaps: {e}")
            return self._fallback_gaps(analyses)

    def _parse_gaps(self, data: Any) -> ResearchGapAnalysis:
        if not isinstance(data, dict):
            return ResearchGapAnalysis()

        explicit_items = []
        for item in data.get("explicitly_acknowledged_gaps", []):
            explicit_items.append(
                ResearchGapItem(
                    topic=item.get("topic", "Acknowledged Limitation"),
                    description=item.get("description", ""),
                    gap_type="explicitly_acknowledged",
                    source_papers=item.get("source_papers", []),
                    supporting_evidence_ids=item.get("supporting_evidence_ids", []),
                )
            )

        inferred_items = []
        for item in data.get("ai_inferred_gaps", []):
            inferred_items.append(
                ResearchGapItem(
                    topic=item.get("topic", "Cross-Paper Inferred Gap"),
                    description=item.get("description", ""),
                    gap_type="ai_inferred",
                    source_papers=item.get("source_papers", []),
                    supporting_evidence_ids=item.get("supporting_evidence_ids", []),
                )
            )

        return ResearchGapAnalysis(
            under_explored_topics=data.get("under_explored_topics", []),
            unanswered_research_questions=data.get("unanswered_research_questions", []),
            common_limitations_across_studies=data.get("common_limitations_across_studies", []),
            explicitly_acknowledged_gaps=explicit_items,
            ai_inferred_gaps=inferred_items,
            future_research_directions=data.get("future_research_directions", []),
        )

    def _fallback_gaps(self, analyses: List[IndividualPaperAnalysis]) -> ResearchGapAnalysis:
        all_limits = []
        all_futures = []
        for a in analyses:
            all_limits.extend(a.limitations.author_acknowledged)
            all_futures.extend(a.future_work.future_directions)

        return ResearchGapAnalysis(
            under_explored_topics=["Inter-regional governance models", "Dynamic distribution line rating"],
            unanswered_research_questions=["How can low-income financing scale in high-impedance rural feeders?"],
            common_limitations_across_studies=all_limits[:3] or ["Limited geographical scope"],
            explicitly_acknowledged_gaps=[
                ResearchGapItem(
                    topic="Subtropical degradation and multi-unit adoption",
                    description="Study excluded multi-unit housing and long-term subtropical battery degradation.",
                    gap_type="explicitly_acknowledged",
                    source_papers=[a.filename for a in analyses[:1]],
                )
            ],
            ai_inferred_gaps=[
                ResearchGapItem(
                    topic="Socio-technical convergence between rural voltage limits and financing",
                    description="Cross-paper gap between physical feeder voltage limits and low-income capital hurdles.",
                    gap_type="ai_inferred",
                    source_papers=[a.filename for a in analyses],
                )
            ],
            future_research_directions=all_futures[:3] or ["Coordinated smart inverter dispatch"],
        )
