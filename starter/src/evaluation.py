"""Retrieval hit accounting and reproducible per-query trace records."""
from __future__ import annotations

import re
from typing import Any


def evaluate_query(question: dict[str, Any], hits: list[dict[str, Any]]) -> dict[str, Any]:
    evidence = re.sub(r"\s+", " ", question["evidence_quote"]).strip().casefold()
    gold_page = question["gold_page"]
    def hit(h: dict[str, Any]) -> bool:
        meta = h["metadata"]
        unit = f"page-{int(meta.get('page', -1)):03}"
        text = re.sub(r"\s+", " ", h["text"]).strip().casefold()
        return meta.get("document_id") == question["gold_source_id"] and unit == gold_page and evidence in text
    return {"question_id": question["id"], "split": question["split"],
            "question": question["question"], "gold_page": gold_page,
            "evidence_quote": evidence, "filter": question.get("filter"), "hits": hits,
            "hit_at_1": bool(hits and hit(hits[0])), "evidence_hit_at_3": any(map(hit, hits))}


def summarize(traces: list[dict[str, Any]]) -> dict[str, Any]:
    out = {}
    for split in ("dev", "test"):
        rows = [t for t in traces if t["split"] == split]
        n = len(rows)
        out[split] = {"n": n,
                      "hit_at_1": {"hits": sum(t["hit_at_1"] for t in rows), "total": n},
                      "evidence_hit_at_3": {"hits": sum(t["evidence_hit_at_3"] for t in rows), "total": n}}
    return out
