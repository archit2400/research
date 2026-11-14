"""PDF parsing using PyMuPDF (fitz) with page-number preservation and scanned document detection."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import pymupdf  # PyMuPDF

class PDFParser:
    """Extracts text page-by-page from academic PDF documents."""

    @staticmethod
    def extract_paper(file_path: Path | str) -> Dict[str, Any]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {path}")

        doc = pymupdf.open(str(path))
        paper_id = path.stem
        total_pages = len(doc)
        pages_data: List[Dict[str, Any]] = []
        total_char_count = 0

        for page_idx in range(total_pages):
            page = doc[page_idx]
            page_text = page.get_text("text").strip()
            total_char_count += len(page_text)
            pages_data.append({
                "page_number": page_idx + 1,
                "text": page_text,
            })

        # Metadata extraction from PDF catalog
        meta = doc.metadata or {}
        doc_title = meta.get("title") or path.stem.replace("_", " ").title()
        doc_author = meta.get("author") or "Not found in paper"

        doc.close()

        # Scanned PDF detection heuristic
        is_scanned = total_pages > 0 and (total_char_count / total_pages) < 50
        if is_scanned:
            for p in pages_data:
                if not p["text"]:
                    p["text"] = "[SCANNED PAGE: No extractable text detected. This document requires OCR processing.]"

        return {
            "paper_id": paper_id,
            "filename": path.name,
            "title": doc_title,
            "author": doc_author,
            "total_pages": total_pages,
            "is_scanned": is_scanned,
            "pages": pages_data,
        }
