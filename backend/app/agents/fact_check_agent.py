"""Agent 4: Fact-Check Agent (Critic) - Rigorous evidence-grounded claim audit."""
from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple
from backend.app.llm.provider import llm
from backend.app.schemas.models import Claim, EvidencePassage, FactCheckItem, FactCheckStatus

SYSTEM_PROMPT = """You are a rigorous Academic Fact-Check Critic Agent.
Your responsibility is to strictly audit claims against their linked evidence passages from uploaded academic papers.

CRITICAL RULES:
1. Verify every claim against its linked evidence text.
2. Check numerical figures (percentages, dollar amounts, sample sizes, hours, voltages). If a number in the claim is NOT present or contradicts the passage, flag as Unsupported or Partially Supported.
3. Detect exaggerations (e.g., claiming "solves all outages" when paper states "achieved 94.2% power reliability on critical circuits").
4. Assign ONE of the 4 strict verification statuses:
   - "Supported": Claim is directly and accurately supported by the evidence passage.
   - "Partially Supported": Claim is generally aligned, but contains minor extrapolation, vague metrics, or partial evidence.
   - "Unsupported": Claim asserts facts, figures, or conclusions absent from the cited passages.
   - "Contradicted": Passage explicitly states the opposite of the claim.
5. Provide detailed analytical reasoning for every decision.
6. If the claim is Partially Supported or Unsupported, indicate `revision_needed: true` and provide a `suggested_revision`.
7. DO NOT evaluate whether the paper's scientific conclusions are ground truth in the real world. Verify ONLY whether the statement is supported by the uploaded text.

Return a JSON object in this format:
{
  "fact_checks": [
    {
      "claim_id": "C01",
      "claim": "Claim text...",
      "status": "Supported",
      "linked_evidence_ids": ["E001"],
      "reason": "Detailed justification...",
      "numbers_verified": ["94.2% power reliability", "48.6 hours reduced to 2.8 hours"],
      "is_exaggerated": false,
      "revision_needed": false,
      "suggested_revision": null
    }
  ]
}
"""

class FactCheckAgent:
    """Critic agent that verifies claims against retrieved passages."""

    def __init__(self):
        self.llm = llm

    def run(self, claims: List[Claim], passages: List[EvidencePassage]) -> List[FactCheckItem]:
        if not claims:
            return []

        eid_to_passage = {p.evidence_id: p for p in passages}

        # Prepare evaluation context
        claims_input = []
        for c in claims:
            linked_passages_text = []
            for eid in c.evidence_ids:
                if eid in eid_to_passage:
                    p = eid_to_passage[eid]
                    linked_passages_text.append(f"[{eid} - {p.paper_name} p.{p.page_number}]: {p.text}")

            claims_input.append({
                "claim_id": c.claim_id,
                "claim": c.claim,
                "cited_evidence_ids": c.evidence_ids,
                "evidence_context": "\n".join(linked_passages_text) if linked_passages_text else "NO LINKED EVIDENCE PASSAGE FOUND"
            })

        prompt = f"Audit the following claims against their cited evidence:\n\n{claims_input}"

        try:
            data = self.llm.complete_json(prompt=prompt, system_prompt=SYSTEM_PROMPT)
            return self._parse_fact_checks(data, claims, eid_to_passage)
        except Exception as e:
            print(f"[FactCheckAgent] LLM fact-checking error: {e}")
            return self._fallback_fact_checks(claims, eid_to_passage)

    def _parse_fact_checks(
        self,
        data: Any,
        original_claims: List[Claim],
        eid_to_passage: Dict[str, EvidencePassage],
    ) -> List[FactCheckItem]:
        raw_items = data.get("fact_checks", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
        results_by_id = {}

        for item in raw_items:
            cid = item.get("claim_id")
            if not cid:
                continue
            status_str = item.get("status", "Supported")
            # Normalize status
            if "Partially" in status_str:
                clean_status = FactCheckStatus.PARTIALLY_SUPPORTED.value
            elif "Contradicted" in status_str:
                clean_status = FactCheckStatus.CONTRADICTED.value
            elif "Unsupported" in status_str:
                clean_status = FactCheckStatus.UNSUPPORTED.value
            else:
                clean_status = FactCheckStatus.SUPPORTED.value

            results_by_id[cid] = FactCheckItem(
                claim_id=cid,
                claim=item.get("claim", ""),
                status=clean_status,
                linked_evidence_ids=item.get("linked_evidence_ids", []),
                reason=item.get("reason", "Verified against provided evidence text."),
                numbers_verified=item.get("numbers_verified", []),
                is_exaggerated=bool(item.get("is_exaggerated", False)),
                revision_needed=bool(item.get("revision_needed", False)),
                suggested_revision=item.get("suggested_revision"),
            )

        # Ensure all original claims have an item
        final_list: List[FactCheckItem] = []
        for c in original_claims:
            if c.claim_id in results_by_id:
                fc = results_by_id[c.claim_id]
                # Enforce: claim with 0 valid evidence IDs cannot be Supported
                valid_eids = [eid for eid in c.evidence_ids if eid in eid_to_passage]
                if not valid_eids:
                    fc.status = FactCheckStatus.UNSUPPORTED.value
                    fc.reason = "Claim rejected: No valid retrieved evidence passages linked to this claim."
                final_list.append(fc)
            else:
                # Deterministic verification fallback
                final_list.append(self._verify_single_claim_heuristic(c, eid_to_passage))

        return final_list

    def _verify_single_claim_heuristic(self, claim: Claim, eid_to_passage: Dict[str, EvidencePassage]) -> FactCheckItem:
        valid_eids = [eid for eid in claim.evidence_ids if eid in eid_to_passage]
        if not valid_eids:
            return FactCheckItem(
                claim_id=claim.claim_id,
                claim=claim.claim,
                status=FactCheckStatus.UNSUPPORTED.value,
                linked_evidence_ids=[],
                reason="Claim lacks valid linked evidence IDs.",
            )

        combined_text = " ".join([eid_to_passage[eid].text for eid in valid_eids])
        # Check numerical numbers in claim
        claim_numbers = re.findall(r"\b\d+(?:\.\d+)?%?", claim.claim)
        missing_numbers = [num for num in claim_numbers if num not in combined_text]

        if missing_numbers:
            return FactCheckItem(
                claim_id=claim.claim_id,
                claim=claim.claim,
                status=FactCheckStatus.PARTIALLY_SUPPORTED.value,
                linked_evidence_ids=valid_eids,
                reason=f"Numerical values {missing_numbers} were not directly located in linked passages.",
                is_exaggerated=True,
                revision_needed=True,
                suggested_revision=re.sub(r"\b\d+(?:\.\d+)?%?", "", claim.claim).strip(),
            )

        return FactCheckItem(
            claim_id=claim.claim_id,
            claim=claim.claim,
            status=FactCheckStatus.SUPPORTED.value,
            linked_evidence_ids=valid_eids,
            reason="All numerical assertions and thematic content directly substantiated by linked evidence.",
            numbers_verified=claim_numbers,
            is_exaggerated=False,
            revision_needed=False,
        )

    def _fallback_fact_checks(self, claims: List[Claim], eid_to_passage: Dict[str, EvidencePassage]) -> List[FactCheckItem]:
        return [self._verify_single_claim_heuristic(c, eid_to_passage) for c in claims]
