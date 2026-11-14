"""Real local multilingual semantic vectors via FastEmbed/ONNX Runtime."""
from __future__ import annotations


class MyEmbedder:
    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2") -> None:
        from fastembed import TextEmbedding
        self.model_name = model_name
        self._model = TextEmbedding(model_name=model_name)
        probe = next(self._model.embed(["kiểm tra kích thước vector"]))
        self.dimensions = len(probe)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [v.tolist() for v in self._model.embed(texts)]

    def embed_query(self, question: str) -> list[float]:
        v = next(self._model.embed([question]))
        return v.tolist()
