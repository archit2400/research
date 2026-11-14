"""Agent 2: Retrieval Agent (RAG) - Fetches relevant passages and assigns unique evidence IDs."""
from __future__ import annotations

from typing import List
from backend.app.rag.vector_store import SessionVectorStore
from backend.app.schemas.models import EvidencePassage

class RetrievalAgent:
    """Agent that executes multi-query semantic retrieval and standardizes evidence passages."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.vector_store = SessionVectorStore(session_id)

    def run(self, sub_queries: List[str], top_k_per_query: int = 4) -> List[EvidencePassage]:
        seen_chunk_ids = set()
        deduped_passages = []

        for query in sub_queries:
            results = self.vector_store.search(query=query, top_k=top_k_per_query)
            for res in results:
                chunk_id = res["chunk_id"]
                if chunk_id in seen_chunk_ids:
                    continue
                seen_chunk_ids.add(chunk_id)
                deduped_passages.append(res)

        # Sort by relevance score descending
        deduped_passages.sort(key=lambda x: x.get("relevance_score", 0.0), reverse=True)

        # Assign clean standardized Evidence IDs: E001, E002, ...
        evidence_list: List[EvidencePassage] = []
        for idx, item in enumerate(deduped_passages, 1):
            eid = f"E{idx:03d}"
            evidence_list.append(
                EvidencePassage(
                    evidence_id=eid,
                    paper_name=item["paper_name"],
                    page_number=item["page_number"],
                    text=item["text"],
                    relevance_score=item.get("relevance_score", 0.0),
                )
            )

        return evidence_list
