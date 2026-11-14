# OCR scan locally without sending the PDF elsewhere

`13nd.signed.pdf` is a 39-page image-only scan. `pypdf` could not extract text from the sampled pages, so OCR is needed before building chunks or a benchmark.

## Local OCR route

The OCR script uses EasyOCR with Vietnamese and English recognition, renders pages locally with Poppler, and writes exactly one text file for each physical PDF page under `data/processed/nd-13-2023/pages_by_pdf/`: `page-001.txt` maps to PDF page 1, and so on. It does not call an OCR website or API. The EasyOCR Python package and its model files must be present on the PC; first-time setup may download dependencies and weights. The PDF itself stays local.

1. From `starter/`, install the Python requirements in the project environment.
2. From the project root, run `python starter/scripts/ocr_pdf.py "C:\path\to\13nd.signed.pdf"`, replacing the example with the PDF's location on your PC.
3. Keep the process running until all 39 pages finish. The script writes one UTF-8 text file per PDF page plus an OCR summary. It does not combine or reflow pages.
4. Review a few pages against the PDF scan, especially headings, article numbers, dates, and tables. OCR can misread diacritics and legal identifiers.

If EasyOCR cannot initialize on Windows because its PyTorch dependency is missing, install a CPU-only PyTorch/torchvision build into the same project environment, then install the remaining requirements. That downloads software/model files only; it does not upload the PDF.

## After OCR

Inspect page boundaries and per-page text lengths, then update `data/manifest.json` with the included physical page IDs and counts. Keep page-specific text even if a page is blank (the corresponding TXT remains empty); exclude cover/blank pages only when calculating substantive content pages. Confirm there are at least 30 eligible pages before proceeding to the benchmark. Keep OCR outputs ignored by Git (`data/processed/`) unless permission to redistribute the scan-derived text has been checked.
