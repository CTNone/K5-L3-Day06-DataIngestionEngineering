"""Build three strategies, retrieve a frozen benchmark, and write traces/metrics."""
from __future__ import annotations

import json
import time
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from .chunking import by_paragraph, fixed_size
from .embeddings import MyEmbedder
from .evaluation import evaluate_query, summarize
from .ingestion import load_corpus, write_manifest
from .store import ChromaVectorStore

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "starter/results"


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def package_version(name: str) -> str | None:
    try:
        return version(name)
    except PackageNotFoundError:
        return None


def main() -> None:
    pages = load_corpus(ROOT)
    if len(pages) != 39:
        raise ValueError(f"Expected 39 page-mapped OCR files; found {len(pages)}")
    content_pages = [p for p in pages if p.page != 1 and p.text.strip()]
    if len(content_pages) < 30:
        raise ValueError(f"Need at least 30 non-cover content pages; found {len(content_pages)}")
    write_manifest(ROOT, pages)
    questions = json.loads((ROOT / "benchmark/questions.json").read_text(encoding="utf-8"))
    if len(questions) < 20 or sum(q["split"] == "dev" for q in questions) < 15 or sum(q["split"] == "test" for q in questions) < 5:
        raise ValueError("Need at least 15 dev and 5 test questions")
    embedder = MyEmbedder("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    store = ChromaVectorStore(RESULTS / "chroma", embedder.dimensions)
    configs = {"A": lambda p: fixed_size(p, 650, 100),
               "B": lambda p: by_paragraph(p, 1400),
               "C": lambda p: by_paragraph(p, 1400)}
    metrics = {"model": embedder.model_name, "dimensions": embedder.dimensions,
               "embedding_library": "FastEmbed", "embedding_library_version": package_version("fastembed"),
               "embedding_warning": "FastEmbed reports this model now uses mean pooling; record this implementation when comparing runs.",
               "chromadb_version": package_version("chromadb"),
               "vector_store": "Chroma PersistentClient", "distance": "cosine", "strategies": {}}
    start_all = time.perf_counter()
    for strategy, chunker in configs.items():
        start = time.perf_counter()
        chunks = [c for p in pages for c in chunker(p)]
        vecs = embedder.embed_documents([c.text for c in chunks])
        store.upsert(strategy, chunks, vecs)
        ingest_seconds = round(time.perf_counter() - start, 3)
        traces = []
        retrieval_seconds = 0.0
        for q in questions:
            query = embedder.embed_query(q["question"])
            t0 = time.perf_counter()
            filters = q.get("filter") if strategy == "C" else None
            hits = store.search(strategy, query, top_k=3, filters=filters)
            retrieval_seconds += time.perf_counter() - t0
            trace = evaluate_query(q, hits)
            trace["strategy"] = strategy
            traces.append(trace)
        summary = summarize(traces)
        trace_path = RESULTS / f"traces_{strategy}.json"
        dump(trace_path, traces)
        metrics["strategies"][strategy] = {
            "chunk_count": len(chunks), "char_count": sum(len(p.text) for p in pages),
            "chunk_chars": {"min": min(map(lambda c: len(c.text), chunks)),
                            "median": sorted(map(lambda c: len(c.text), chunks))[len(chunks)//2],
                            "max": max(map(lambda c: len(c.text), chunks))},
            "ingest_seconds": ingest_seconds, "retrieval_seconds_total": round(retrieval_seconds, 3),
            "cost_usd": 0, "summary": summary, "trace_file": str(trace_path.relative_to(ROOT))}
        print(strategy, json.dumps(metrics["strategies"][strategy]["summary"], ensure_ascii=False))
    metrics["total_runtime_seconds"] = round(time.perf_counter() - start_all, 3)
    metrics["run_status"] = "complete"
    metrics.pop("run_note", None)
    metrics["human_assessment"] = "Pending: 10 matched coherence positions per strategy; 5 test questions for metadata and grounding. See report/manual-review-template.csv."
    dump(RESULTS / "metrics.json", metrics)
    dump(RESULTS / "benchmark_snapshot.json", questions)
    print(f"Wrote {RESULTS / 'metrics.json'}")


if __name__ == "__main__":
    main()
