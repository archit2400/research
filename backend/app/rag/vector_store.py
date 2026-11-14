"""Session-isolated vector store using ChromaDB and SentenceTransformer embeddings."""
from __future__ import annotations

import threading
from typing import Any, Dict, List, Optional
import chromadb
from chromadb.utils import embedding_functions

from backend.app.config import settings
from backend.app.schemas.models import EvidencePassage

_client_lock = threading.Lock()
_chroma_client: Optional[chromadb.ClientAPI] = None
_embedding_fn = None

def get_chroma_client() -> chromadb.ClientAPI:
    """Singleton Chroma client."""
    global _chroma_client, _embedding_fn
    with _client_lock:
        if _chroma_client is None:
            settings.CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
            _chroma_client = chromadb.PersistentClient(path=str(settings.CHROMA_PERSIST_DIR))
            _embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=settings.EMBEDDING_MODEL
            )
        return _chroma_client

def get_embedding_function():
    get_chroma_client()
    return _embedding_fn

class SessionVectorStore:
    """Manages an isolated ChromaDB collection per research session."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        # Collection name must be alphanumeric with underscores/hyphens
        clean_id = "".join(c if c.isalnum() else "_" for c in session_id)
        self.collection_name = f"session_{clean_id}"
        self.client = get_chroma_client()
        self.embedding_fn = get_embedding_function()
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        """Add text chunks into the session's isolated collection."""
        if not chunks:
            return 0

        ids = [c["chunk_id"] for c in chunks]
        documents = [c["text"] for c in chunks]
        metadatas = [
            {
                "paper_id": c["paper_id"],
                "paper_name": c["paper_name"],
                "paper_title": c.get("paper_title", c["paper_name"]),
                "page_number": int(c["page_number"]),
            }
            for c in chunks
        ]

        self.collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
        return len(chunks)

    def search(self, query: str, top_k: int = settings.RETRIEVAL_TOP_K) -> List[Dict[str, Any]]:
        """Retrieve most semantically similar chunks for a query."""
        count = self.collection.count()
        if count == 0:
            return []

        k = min(top_k, count)
        results = self.collection.query(
            query_texts=[query],
            n_results=k,
            include=["documents", "metadatas", "distances"]
        )

        passages: List[Dict[str, Any]] = []
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]
        ids = results.get("ids", [[]])[0]

        for i, doc_text in enumerate(docs):
            dist = distances[i] if i < len(distances) else 0.5
            meta = metas[i] if i < len(metas) else {}
            # Cosine distance to similarity: 1.0 - (dist / 2) or max(0, 1 - dist)
            relevance = round(max(0.0, 1.0 - float(dist)), 3)

            passages.append({
                "chunk_id": ids[i],
                "paper_id": meta.get("paper_id", ""),
                "paper_name": meta.get("paper_name", "Paper"),
                "paper_title": meta.get("paper_title", meta.get("paper_name", "")),
                "page_number": int(meta.get("page_number", 1)),
                "text": doc_text,
                "relevance_score": relevance,
            })

        return passages

    def clear(self):
        """Delete session collection when research session ends."""
        try:
            self.client.delete_collection(name=self.collection_name)
        except Exception:
            pass
