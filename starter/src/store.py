"""Persistent local Chroma store with cosine similarity and metadata filtering."""
from __future__ import annotations

from pathlib import Path
from typing import Any
try:
    import chromadb
except ImportError:
    chromadb = None
from .models import Chunk


class ChromaVectorStore:
    def __init__(self, path: Path, dimensions: int) -> None:
        if chromadb is None:
            raise RuntimeError("Chroma is not installed. Run: python -m pip install -r requirements.txt")
        self.path = Path(path)
        self.path.mkdir(parents=True, exist_ok=True)
        self.dimensions = dimensions
        self.client = chromadb.PersistentClient(path=str(self.path))

    def collection(self, strategy: str):
        return self.client.get_or_create_collection(
            name=f"day6_{strategy.lower()}", metadata={"hnsw:space": "cosine"})

    def upsert(self, strategy: str, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        if len(chunks) != len(vectors):
            raise ValueError("chunk/vector count mismatch")
        col = self.collection(strategy)
        if chunks:
            ids = [f"{strategy}:{c.chunk_id}" for c in chunks]
            metas = []
            for c in chunks:
                meta = {k: v for k, v in c.metadata.items() if isinstance(v, (str, int, float, bool))}
                meta.update({"document_id": c.document_id, "source": c.source,
                             "page": c.page, "strategy": strategy})
                metas.append(meta)
            col.upsert(ids=ids, documents=[c.text for c in chunks], embeddings=vectors, metadatas=metas)

    def search(self, strategy: str, query_vector: list[float], top_k: int = 3,
               filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        where = None
        if filters:
            where = {k: v for k, v in filters.items() if v is not None}
        result = self.collection(strategy).query(query_embeddings=[query_vector], n_results=top_k,
                                                  where=where, include=["documents", "metadatas", "distances"])
        hits = []
        for i, cid in enumerate(result["ids"][0]):
            meta = result["metadatas"][0][i] or {}
            hits.append({"chunk_id": cid, "text": result["documents"][0][i],
                         "score": 1.0 - float(result["distances"][0][i]), "metadata": meta})
        return hits
