# Starter · local Chroma + multilingual embedding

Bộ khởi động lab được hiện thực theo corpus Nghị định 13/2023/NĐ-CP. Tài liệu PDF là scan; benchmark được lưu tại `../benchmark/questions.json`. Bản OCR nằm ở `../data/processed/nd-13-2023/pages_by_pdf/` trên máy người học và được Git bỏ qua; để tái tạo, tải PDF từ liên kết Chính phủ trong manifest rồi chạy script OCR. Xem [manifest](../data/manifest.json) và [mẫu báo cáo](../REPORT_TEMPLATE.md) để ghi nguồn và giới hạn xác minh.

## Kiến trúc

- **Nguồn:** đúng 39 TXT, ánh xạ trực tiếp từng trang PDF: `pages_by_pdf/page-001.txt` = trang PDF 1, ..., `page-039.txt` = trang 39.
- **Embedding:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` qua FastEmbed/ONNX, chạy local; cùng một encoder cho query và document; chiều vector được đọc từ model lúc khởi tạo.
- **Vector store:** Chroma persistent, cosine similarity, metadata filter; dữ liệu lưu tại `results/chroma/`.
- **Chiến lược:** A cửa sổ 650 ký tự, overlap 100; B theo đoạn, tối đa 1.400 ký tự; C giống B nhưng lọc `chapter` khi benchmark đưa filter.
- **Benchmark:** 20 câu cố định (15 dev, 5 test) tại `../benchmark/questions.json`; top-3 trace và metrics lưu trong `results/`.

## Cài và chạy trên Windows PowerShell

```powershell
cd starter
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m src.run
```

Nếu PowerShell đang ở thư mục gốc dự án, trước hết chạy `cd .\starter`, rồi chạy `.\.venv\Scripts\python.exe -m src.run`.

Lần chạy đầu FastEmbed cần tải model embedding về máy; model đã được tải và pipeline A/B/C đã chạy hoàn tất. Không cần Docker, API key hoặc gửi tài liệu tới dịch vụ embedding. Muốn tái chạy, vector được upsert theo ID ổn định, không nhân đôi.

## Đầu ra

- `results/metrics.json`: số chunk, kích thước, thời gian, chi phí và Hit@1/Evidence Hit@3 chia dev/test.
- `results/traces_A.json`, `traces_B.json`, `traces_C.json`: câu hỏi, filter, top-3 text/score/metadata và gold evidence.
- `results/benchmark_snapshot.json`: bộ câu hỏi đóng băng khi chạy.
- `results/chroma/`: vector store bền vững (bỏ qua bởi Git).

## OCR và giới hạn hiện tại

PDF chính thức là 39 trang ảnh. pypdf không trích được chữ. Bộ TXT đúng trang đã được OCR tại `data/processed/nd-13-2023/pages_by_pdf/` và bị Git bỏ qua. Benchmark tracked tại `../benchmark/questions.json` trỏ đến số trang PDF thật; evidence được kiểm tra có trong đúng tệp gold, nhưng cần người rà lại nội dung OCR. Không gửi PDF sang website OCR.
