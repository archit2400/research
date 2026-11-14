"""Export research report to standard academic Markdown format."""
from __future__ import annotations

from backend.app.schemas.models import ResearchPipelineResult

def generate_markdown_report(result: ResearchPipelineResult) -> str:
    md = []
    md.append(f"# ResearchPilot Academic Intelligence Report")
    md.append(f"**Research Question:** {result.question}\n")
    md.append(f"> **Epistemological Disclaimer:** {result.disclaimer}\n")
    md.append("---\n")

    # Section 1: Literature Review
    md.append("## 1. Literature Review & Thematic Synthesis\n")
    for theme in result.literature_review.themes:
        md.append(f"### {theme.theme}\n")
        for claim in theme.claims:
            eids_str = ", ".join([f"[{eid}]" for eid in claim.evidence_ids])
            papers_str = ", ".join(claim.cited_papers)
            pages_str = ", ".join([f"p. {p}" for p in claim.cited_pages])
            md.append(f"- **{claim.claim}**")
            md.append(f"  - *Citations:* {eids_str} | Source: {papers_str} ({pages_str})")
            if claim.evidence_quotes:
                md.append(f"  - *Evidence Quote:* \"{claim.evidence_quotes[0]}\"")
        md.append("")

    # Section 2: Cross-Paper Comparison
    md.append("## 2. Cross-Paper Comparison Matrix\n")
    md.append("| Paper Title | Research Objectives | Methodology | Datasets & Settings | Results & Conclusions |")
    md.append("|---|---|---|---|---|")
    for row in result.cross_paper_comparison.matrix:
        clean_title = row.paper_title.replace("|", "/")
        clean_obj = row.objectives.replace("|", "/")
        clean_meth = row.methodologies.replace("|", "/")
        clean_data = row.datasets_and_settings.replace("|", "/")
        clean_res = row.results_and_conclusions.replace("|", "/")
        md.append(f"| {clean_title} | {clean_obj} | {clean_meth} | {clean_data} | {clean_res} |")
    md.append("")

    # Section 3: Verified Claims
    md.append("## 3. Verified Claims Audit\n")
    for vc in result.verified_claims:
        md.append(f"- `[{vc.claim_id}]` **{vc.claim}**")
        md.append(f"  - *Critic Verification:* {vc.critic_reasoning or 'Verified against document text'}")
        if vc.evidence_ids:
            md.append(f"  - *Evidence IDs:* {', '.join(vc.evidence_ids)}")
    md.append("")

    # Section 4: Dropped / Unsupported Claims
    md.append("## 4. Unsupported and Excluded Claims\n")
    if not result.dropped_claims:
        md.append("*No claims were dropped. All assertions satisfied evidence-grounding thresholds.*")
    else:
        for dc in result.dropped_claims:
            md.append(f"- `[{dc.claim_id}]` **{dc.claim}**")
            md.append(f"  - *Status:* {dc.status}")
            md.append(f"  - *Rejection Reason:* {dc.reason}")
    md.append("")

    # Section 5: Contradiction Analysis
    md.append("## 5. Cross-Paper Contradiction Analysis\n")
    if not result.contradiction_analysis:
        md.append("*No direct empirical contradictions detected across the analyzed papers.*")
    else:
        for i, c in enumerate(result.contradiction_analysis, 1):
            md.append(f"### Disagreement {i}: {c.topic}\n")
            md.append(f"- **Position A ({c.source_a_paper}, p.{c.source_a_page}):** {c.position_a}")
            if c.source_a_quote:
                md.append(f"  > \"{c.source_a_quote}\"")
            md.append(f"- **Position B ({c.source_b_paper}, p.{c.source_b_page}):** {c.position_b}")
            if c.source_b_quote:
                md.append(f"  > \"{c.source_b_quote}\"")
            md.append(f"- **Methodological Explanation:** {c.explanation_of_divergence}\n")

    # Section 6: Research Gaps
    md.append("## 6. Research Gaps & Future Directions\n")
    md.append("### Acknowledged Gaps (From Authors)")
    for eg in result.research_gaps.explicitly_acknowledged_gaps:
        md.append(f"- **{eg.topic}:** {eg.description} (Reported in: {', '.join(eg.source_papers)})")
    md.append("\n### AI-Inferred Gaps")
    for ig in result.research_gaps.ai_inferred_gaps:
        md.append(f"- **{ig.topic}:** {ig.description}")
    md.append("\n### Future Directions")
    for i, fd in enumerate(result.research_gaps.future_research_directions, 1):
        md.append(f"{i}. {fd}")
    md.append("")

    # Section 7: Evidence Explorer
    md.append("## 7. Evidence Passages Appendix\n")
    for ep in result.sources_and_evidence:
        md.append(f"### `[{ep.evidence_id}]` {ep.paper_name} (Page {ep.page_number})")
        md.append(f"```text\n{ep.text.strip()}\n```\n")

    return "\n".join(md)
