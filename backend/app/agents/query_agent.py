"""Agent 1: Query Agent - Decomposes research question into 4-8 targeted sub-queries."""
from __future__ import annotations

from typing import List
from backend.app.llm.provider import llm

SYSTEM_PROMPT = """You are an expert Academic Query Decomposition Agent.
Your job is to analyze a user's research question and decompose it into 4 to 8 distinct, comprehensive, and non-overlapping sub-queries for semantic retrieval over academic literature.

Cover different analytical dimensions:
1. Core theoretical definitions, mechanisms, and architectures.
2. Empirical methodologies, experimental testbeds, and simulation settings.
3. Quantitative results, metrics (e.g., percentages, financial costs, reliability indices).
4. Structural barriers, governance/regulatory constraints, or economic viability.
5. Grid topology variations (e.g., urban vs. rural, high vs. low penetration).
6. Limitations, outage survival, and future research challenges.

Return a JSON object with this exact structure:
{
  "sub_queries": [
    "sub-query 1",
    "sub-query 2",
    "sub-query 3",
    "sub-query 4"
  ]
}
"""

class QueryAgent:
    """Agent that formulates search sub-queries to guide the Retrieval Agent."""

    def __init__(self):
        self.llm = llm

    def run(self, research_question: str) -> List[str]:
        prompt = f"Research Question: {research_question}\n\nGenerate 4-8 focused, high-precision search sub-queries."
        try:
            data = self.llm.complete_json(prompt=prompt, system_prompt=SYSTEM_PROMPT)
            if isinstance(data, dict) and "sub_queries" in data:
                queries = [q.strip() for q in data["sub_queries"] if isinstance(q, str) and q.strip()]
                if len(queries) >= 3:
                    return queries[:8]
            elif isinstance(data, list):
                queries = [q.strip() for q in data if isinstance(q, str) and q.strip()]
                if len(queries) >= 3:
                    return queries[:8]
        except Exception as e:
            print(f"[QueryAgent] Warning: LLM query generation encountered error: {e}")

        # Deterministic fallback sub-queries
        return [
            f"Core mechanisms and problem definitions regarding {research_question}",
            f"Empirical methodology, datasets, and experimental findings for {research_question}",
            f"Quantitative metrics, percentage improvements, and numerical results on {research_question}",
            f"Economic, governance, and technical limitations related to {research_question}",
            f"Comparative outcomes across different operating environments for {research_question}",
        ]
