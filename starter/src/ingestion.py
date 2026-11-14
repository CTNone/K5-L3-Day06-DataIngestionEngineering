"""Load normalized, page-addressable corpus units and official local text files."""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from .models import DocumentPage


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFC", text).replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def load_pdf(path: Path, document_id: str, source: str) -> list[DocumentPage]:
    from pypdf import PdfReader
    result = []
    for num, page in enumerate(PdfReader(str(path)).pages, start=1):
        text = normalize_text(page.extract_text() or "")
        if text:
            result.append(DocumentPage(document_id, source, num, text,
                                       {"chapter": "unknown", "document_type": "decree"}))
    return result


def load_corpus(root: Path) -> list[DocumentPage]:
    """Read one TXT per PDF page, preserving its physical page number."""
    pages_dir = root / "data/processed/nd-13-2023/pages_by_pdf"
    files = [pages_dir / f"page-{n:03}.txt" for n in range(1, 40)]
    if not pages_dir.is_dir() or not all(f.is_file() for f in files):
        raise FileNotFoundError(f"No source unit text files in {pages_dir}")
    pages = []
    for f in files:
        text = normalize_text(f.read_text(encoding="utf-8"))
        n = int(re.search(r"(\d+)", f.stem).group(1))
        if 2 <= n <= 6:
            chapter = "Chương I"
        elif 7 <= n <= 23:
            chapter = "Chương II"
        elif n == 24:
            chapter = "Chương II-III"
        elif 25 <= n <= 26:
            chapter = "Chương III"
        elif n == 27:
            chapter = "Chương III-IV"
        elif n == 28:
            chapter = "Chương IV"
        elif 29 <= n <= 39:
            chapter = "Phụ lục"
        else:
            chapter = "Trang đầu"
        pages.append(DocumentPage("nd-13-2023", "Chính phủ: Nghị định 13/2023/NĐ-CP",
                                  n, text, {"chapter": chapter, "document_type": "decree",
                                            "page_id": f"page-{n:03}"}))
    return pages


def write_manifest(root: Path, pages: list[DocumentPage]) -> None:
    manifest = json.loads((root / "data/manifest.json").read_text(encoding="utf-8"))
    src = manifest["sources"][0]
    src["source_path_or_url"] = "https://vanban.chinhphu.vn/?docid=207759&pageid=27160"
    src["text_full_version_url"] = "https://xaydungchinhsach.chinhphu.vn/toan-van-nghi-dinh-13-2023-nd-cp-bao-ve-du-lieu-ca-nhan-119230516104357809.htm"
    src["accessed_at"] = "2026-11-13"
    src["physical_page_count"] = 39
    src["counting_rule"] = "Use all 39 physical PDF pages, including the opening page and annex forms. One UTF-8 TXT per page: page-001.txt is PDF page 1, ..., page-039.txt is page 39."
    src["physical_page_count"] = 39
    src["included_page_ids"] = [f"page-{p.page:03}" for p in pages if p.text.strip()]
    src["page_char_counts"] = {f"page-{p.page:03}": len(p.text) for p in pages}
    src["license_or_permission"] = "Official public legal text; redistributing portal transcription still requires attribution per portal footer. Keep processed corpus local until redistribution rights checked."
    summary_path = root / "data/processed/nd-13-2023/pages_by_pdf/ocr_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else {}
    src["ocr"] = {"status": "complete_needs_human_review" if summary.get("page_count") == 39 else "incomplete", "reason": "EasyOCR local CPU completed 39/39 physical pages at 260 DPI. Review low-confidence pages, especially annex forms.", "tool": "EasyOCR local CPU, vi+en; Poppler pdftoppm", "processing_location": "On the learner's PC; no OCR website/API was called during this run.", "human_review_required": True, "output_directory": "data/processed/nd-13-2023/pages_by_pdf/", "page_count": summary.get("page_count", len(pages)), "dpi": summary.get("dpi", 260), "summary": "data/processed/nd-13-2023/pages_by_pdf/ocr_summary.json"}
    (root / "data/manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
