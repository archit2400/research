"""Agent 6: Writer Agent - Compiles verified literature review and dropped claims log."""
from __future__ import annotations

from typing import Dict, List, Tuple
from backend.app.schemas.models import (
    Claim,
    ContradictionItem,
    DroppedClaim,
    FactCheckItem,
    FactCheckStatus,
    LiteratureReview,
    LiteratureTheme,
    ResearchGapAnalysis,
)

class WriterAgent:
    """Agent that synthesizes final academic literature review using ONLY verified claims."""

    def run(
        self,
        original_review: LiteratureReview,
        fact_checks: List[FactCheckItem],
        contradictions: List[ContradictionItem],
        gaps: ResearchGapAnalysis,
    ) -> Tuple[LiteratureReview, List[Claim], List[DroppedClaim]]:
        fc_map: Dict[str, FactCheckItem] = {fc.claim_id: fc for fc in fact_checks}

        verified_claims: List[Claim] = []
        dropped_claims: List[DroppedClaim] = []
        final_themes: List[LiteratureTheme] = []

        for theme_block in original_review.themes:
            approved_theme_claims: List[Claim] = []

            for claim in theme_block.claims:
                fc = fc_map.get(claim.claim_id)

                # Strict acceptance criteria: Must be Supported and have at least 1 valid evidence ID
                if fc and fc.status == FactCheckStatus.SUPPORTED.value and claim.evidence_ids:
                    # Update claim with critic verified details
                    claim.verification_status = FactCheckStatus.SUPPORTED.value
                    claim.critic_reasoning = fc.reason
                    approved_theme_claims.append(claim)
                    verified_claims.append(claim)
                else:
                    # Claim dropped!
                    reason = fc.reason if fc else "Claim omitted: Lacks verified evidence grounding."
                    status = fc.status if fc else FactCheckStatus.UNSUPPORTED.value
                    dropped_claims.append(
                        DroppedClaim(
                            claim_id=claim.claim_id,
                            claim=claim.claim,
                            status=status,
                            reason=reason,
                            discrepancies=[f"Missing numbers or unverified assertions: {reason}"] if "number" in reason.lower() else [],
                        )
                    )

            if approved_theme_claims:
                final_themes.append(
                    LiteratureTheme(
                        theme=theme_block.theme,
                        claims=approved_theme_claims,
                    )
                )

        final_review = LiteratureReview(themes=final_themes)
        return final_review, verified_claims, dropped_claims
