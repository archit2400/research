"""Agent 3: Summary Agent - Thematic synthesis linking every claim to Evidence IDs."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from backend.app.llm.provider import llm
from backend.app.schemas.models import Claim, EvidencePassage, LiteratureReview, LiteratureTheme

SYSTEM_PROMPT = """You are an expert Academic Summary Agent.
Your role is to synthesize evidence passages from uploaded academic papers into a structured, theme-based literature review.

STRICT RULES:
1. Group findings into 2-4 comprehensive academic themes (e.g., 'Resilience Metrics and Storage Scheduling', 'Economic Viability and Regulatory Attrition', 'Grid Topology and Feeder Stress').
2. Every factual assertion must be an individual claim item.
3. Every claim MUST cite the exact `evidence_ids` (e.g. ["E001", "E002"]) from the provided evidence list. DO NOT invent evidence IDs.
4. Distinguish between statements that are explicitly stated in the paper vs. AI-inferred conclusions.
5. Extract verbatim supporting quotes from the evidence passages.
6. Include specific quantitative metrics, sample sizes, and percentages found in the evidence.

Return a JSON object in this exact format:
{
  "themes": [
    {
      "theme": "Theme Title",
      "claims": [
        {
          "claim_id": "C01",
          "claim": "Direct factual assertion with numbers...",
          "evidence_ids": ["E001"],
          "cited_papers": ["paper1.pdf"],
          "cited_pages": [1],
          "statement_type": "explicitly_stated",
          "evidence_quotes": ["Verbatim sentence from passage..."]
        }
      ]
    }
  ]
}
"""

REVISION_PROMPT = """You are revising the literature review claims based on feedback from the Fact-Check Critic Agent.
Review the critic's feedback on unsupported or partially supported claims and revise the claims so that they strictly match the cited evidence without exaggeration.
If a claim cannot be supported by any provided passage, do not include it.

Critic Feedback:
{feedback}

Provided Evidence Passages:
{evidence_context}

Return the revised JSON object matching the same theme schema.
"""

class SummaryAgent:
    """Agent that synthesizes retrieved evidence into themed claims with strict evidence mapping."""

    def __init__(self):
        self.llm = llm

    def _format_evidence_context(self, passages: List[EvidencePassage]) -> str:
        lines = []
        for p in passages:
            lines.append(f"[{p.evidence_id}] Paper: {p.paper_name} (Page {p.page_number})")
            lines.append(f"Text: {p.text.strip()}")
            lines.append("-" * 40)
        return "\n".join(lines)

    def run(self, question: str, passages: List[EvidencePassage]) -> LiteratureReview:
        evidence_text = self._format_evidence_context(passages)
        prompt = (
            f"Research Question: {question}\n\n"
            f"Available Evidence Passages ({len(passages)} passages):\n"
            f"{evidence_text}\n\n"
            f"Generate the themed academic literature review with claim-level evidence IDs."
        )

        try:
            data = self.llm.complete_json(prompt=prompt, system_prompt=SYSTEM_PROMPT)
            return self._parse_review(data, passages)
        except Exception as e:
            print(f"[SummaryAgent] Error generating review: {e}")
            return self._fallback_review(passages)

    def revise(self, review: LiteratureReview, feedback: str, passages: List[EvidencePassage]) -> LiteratureReview:
        evidence_text = self._format_evidence_context(passages)
        prompt = REVISION_PROMPT.format(feedback=feedback, evidence_context=evidence_text)
        try:
            data = self.llm.complete_json(prompt=prompt, system_prompt=SYSTEM_PROMPT)
            return self._parse_review(data, passages)
        except Exception as e:
            print(f"[SummaryAgent] Error during revision: {e}")
            return review

    def _parse_review(self, data: Any, passages: List[EvidencePassage]) -> LiteratureReview:
        valid_eids = {p.evidence_id for p in passages}
        eid_to_passage = {p.evidence_id: p for p in passages}

        theme_list: List[LiteratureTheme] = []
        raw_themes = data.get("themes", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])

        claim_counter = 1
        for t_idx, t in enumerate(raw_themes):
            theme_title = t.get("theme", f"Theme {t_idx + 1}")
            claims: List[Claim] = []

            for c in t.get("claims", []):
                cid = c.get("claim_id", f"C{claim_counter:02d}")
                claim_text = c.get("claim", "").strip()
                if not claim_text:
                    continue

                raw_eids = c.get("evidence_ids", [])
                matched_eids = [eid for eid in raw_eids if eid in valid_eids]
                
                # Derive cited papers and pages if not explicitly provided
                cited_papers = c.get("cited_papers", [])
                cited_pages = c.get("cited_pages", [])
                quotes = c.get("evidence_quotes", [])

                if matched_eids and (not cited_papers or not cited_pages):
                    cited_papers = list({eid_to_passage[eid].paper_name for eid in matched_eids})
                    cited_pages = sorted(list({eid_to_passage[eid].page_number for eid in matched_eids}))

                claims.append(
                    Claim(
                        claim_id=cid,
                        claim=claim_text,
                        evidence_ids=matched_eids,
                        cited_papers=cited_papers,
                        cited_pages=cited_pages,
                        statement_type=c.get("statement_type", "explicitly_stated"),
                        evidence_quotes=quotes,
                    )
                )
                claim_counter += 1

            if claims:
                theme_list.append(LiteratureTheme(theme=theme_title, claims=claims))

        return LiteratureReview(themes=theme_list)

    def _fallback_review(self, passages: List[EvidencePassage]) -> LiteratureReview:
        # Fallback when LLM fails: construct basic review directly from top passages
        claims = []
        for i, p in enumerate(passages[:4], 1):
            claims.append(
                Claim(
                    claim_id=f"C{i:02d}",
                    claim=f"Evidence from {p.paper_name} (p. {p.page_number}) indicates: {p.text[:140]}...",
                    evidence_ids=[p.evidence_id],
                    cited_papers=[p.paper_name],
                    cited_pages=[p.page_number],
                    statement_type="explicitly_stated",
                    evidence_quotes=[p.text[:120]],
                )
            )
        return LiteratureReview(themes=[LiteratureTheme(theme="Primary Empirical Findings", claims=claims)])
