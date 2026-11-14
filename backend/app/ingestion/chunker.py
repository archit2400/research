"""Semantic text chunking with configurable overlap and metadata preservation."""
from __future__ import annotations

from typing import Any, Dict, List
from backend.app.config import settings

class DocumentChunker:
    """Splits extracted PDF pages into overlapping chunks preserving page and paper metadata."""

    def __init__(self, chunk_size: int = settings.CHUNK_SIZE, overlap: int = settings.CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_paper(self, paper_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        paper_id = paper_data["paper_id"]
        filename = paper_data["filename"]
        title = paper_data.get("title", filename)
        chunks: List[Dict[str, Any]] = []

        for p in paper_data.get("pages", []):
            page_num = p["page_number"]
            page_text = p["text"].strip()
            if not page_text:
                continue

            # If page text is within chunk size, keep as single chunk
            if len(page_text) <= self.chunk_size:
                chunks.append({
                    "chunk_id": f"{paper_id}_p{page_num}_c0",
                    "paper_id": paper_id,
                    "paper_name": filename,
                    "paper_title": title,
                    "page_number": page_num,
                    "text": page_text,
                })
                continue

            # Sliding window chunking
            start = 0
            chunk_idx = 0
            while start < len(page_text):
                end = start + self.chunk_size
                # Try finding natural sentence break near end
                if end < len(page_text):
                    period_pos = page_text.rfind(". ", start, end)
                    if period_pos != -1 and period_pos > start + 100:
                        end = period_pos + 1
                    else:
                        newline_pos = page_text.rfind("\n", start, end)
                        if newline_pos != -1 and newline_pos > start + 100:
                            end = newline_pos

                chunk_str = page_text[start:end].strip()
                if chunk_str:
                    chunks.append({
                        "chunk_id": f"{paper_id}_p{page_num}_c{chunk_idx}",
                        "paper_id": paper_id,
                        "paper_name": filename,
                        "paper_title": title,
                        "page_number": page_num,
                        "text": chunk_str,
                    })
                    chunk_idx += 1

                start = end - self.overlap
                if start >= len(page_text) or end >= len(page_text):
                    break

        return chunks
