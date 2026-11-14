"""Three strategies: fixed windows, article-aware paragraphs, and B+metadata filter."""
from __future__ import annotations

import re
from .models import Chunk, DocumentPage


def fixed_size(page: DocumentPage, size: int = 650, overlap: int = 100) -> list[Chunk]:
    if size <= 0 or overlap < 0 or overlap >= size:
        raise ValueError("Require size > overlap >= 0")
    text = page.text.strip()
    chunks: list[Chunk] = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            boundary = text.rfind(" ", start + size // 2, end)
            if boundary > start:
                end = boundary
        body = text[start:end].strip()
        if body:
            chunks.append(_chunk(page, len(chunks), body, start, end))
        if end >= len(text):
            break
        start = max(start + 1, end - overlap)
    return chunks


def by_paragraph(page: DocumentPage, max_size: int = 1400) -> list[Chunk]:
    if max_size <= 0:
        raise ValueError("max_size must be positive")
    # OCR preserves detected text lines more reliably than paragraph blank lines.
    # Group line units up to max_size so article/line structure stays readable.
    paragraphs = [p.strip() for p in page.text.splitlines() if p.strip()]
    chunks: list[Chunk] = []
    current: list[str] = []
    length = 0
    offset = 0
    for para in paragraphs:
        pieces = [para[i:i + max_size] for i in range(0, len(para), max_size)]
        for piece in pieces:
            separator_length = 2 if current else 0  # "\n\n" between grouped OCR lines
            if current and length + separator_length + len(piece) > max_size:
                body = "\n\n".join(current)
                chunks.append(_chunk(page, len(chunks), body, offset, offset + len(body)))
                offset += len(body)
                current, length = [], 0
            current.append(piece)
            length += (2 if len(current) > 1 else 0) + len(piece)
    if current:
        body = "\n\n".join(current)
        chunks.append(_chunk(page, len(chunks), body, offset, offset + len(body)))
    return chunks


def _chunk(page: DocumentPage, index: int, text: str, start: int, end: int) -> Chunk:
    meta = dict(page.metadata)
    meta.update({"char_start": start, "char_end": end})
    return Chunk(f"{page.document_id}:{page.page}:{index}:{start}", page.document_id,
                 page.source, page.page, text, meta)
