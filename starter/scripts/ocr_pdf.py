"""Run Vietnamese OCR locally on a scanned PDF and keep output aligned by page."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from easyocr import Reader

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def page_number(path: Path) -> int:
    return int(path.stem.rsplit("-", 1)[1])


def find_pdftoppm() -> str | None:
    """Find Poppler from PATH or common local Windows installs."""
    found = shutil.which("pdftoppm") or shutil.which("pdftoppm.exe")
    if found:
        return found
    candidates = [
        Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe",
        Path.home() / ".cache/codex-runner/dependencies/native/poppler/Library/bin/pdftoppm.exe",
        Path("C:/Program Files/poppler/Library/bin/pdftoppm.exe"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path, help="Scanned PDF path")
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "data/processed/nd-13-2023/pages_by_pdf")
    parser.add_argument("--dpi", type=int, default=260)
    args = parser.parse_args()

    pdf = args.pdf.expanduser().resolve()
    if not pdf.is_file():
        parser.error(f"PDF not found: {pdf}")
    poppler = find_pdftoppm()
    if not poppler:
        raise SystemExit("pdftoppm (Poppler) is required to render PDF pages locally.")
    if args.dpi < 150 or args.dpi > 400:
        parser.error("--dpi must be between 150 and 400")

    args.output.mkdir(parents=True, exist_ok=True)
    model_dir = PROJECT_ROOT / "data/processed/easyocr_models"
    model_dir.mkdir(parents=True, exist_ok=True)

    print("Initializing local Vietnamese/English OCR model; the first run may fetch model weights.")
    reader = Reader(["vi", "en"], gpu=False, model_storage_directory=str(model_dir))
    summary: list[dict[str, object]] = []

    with tempfile.TemporaryDirectory(prefix="day6-ocr-") as temp_dir:
        prefix = Path(temp_dir) / "page"
        subprocess.run([poppler, "-png", "-r", str(args.dpi), str(pdf), str(prefix)], check=True)
        images = sorted(Path(temp_dir).glob("page-*.png"), key=page_number)
        if not images:
            raise SystemExit("Poppler did not render any pages.")

        for index, image in enumerate(images, start=1):
            results = reader.readtext(str(image), detail=1, paragraph=False)
            lines = [str(item[1]).strip() for item in results if len(item) > 1 and str(item[1]).strip()]
            text = "\n".join(lines)
            confidences = [float(item[2]) for item in results if len(item) > 2]
            target = args.output / f"page-{index:03}.txt"
            target.write_text(text + "\n", encoding="utf-8")
            summary.append({
                "page": index,
                "characters": len(text),
                "line_count": len(lines),
                "mean_line_confidence": round(sum(confidences) / len(confidences), 4) if confidences else None,
                "text_file": str(target),
                "status": "ocr_complete" if text.strip() else "empty_or_ocr_failed",
            })
            print(f"Page {index}/{len(images)}: {len(text)} characters")

    result = {
        "source_pdf": str(pdf),
        "engine": "EasyOCR local CPU",
        "languages": ["vi", "en"],
        "dpi": args.dpi,
        "page_count": len(summary),
        "pages": summary,
    }
    (args.output / "ocr_summary.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"OCR complete. One TXT per physical PDF page: {args.output.resolve()}")


if __name__ == "__main__":
    main()
