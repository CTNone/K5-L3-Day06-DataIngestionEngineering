# Báo cáo cá nhân — Day 06: Data Ingestion Engineering

- Họ và tên: Chu Thân Nhất
- MSSV: 2A202603649
- Lớp: L3A
- Corpus: Nghị định 13/2023/NĐ-CP, PDF scan 39 trang.
- Repo dự kiến: https://github.com/CTNone/K5-L3-Day06-DataIngestionEngineering

## 1. Corpus và OCR

Tôi dùng toàn bộ 39 trang vật lý, gồm trang mở đầu và biểu mẫu phụ lục. OCR tạo một tệp UTF-8 cho mỗi trang (`page-001.txt` tương ứng PDF trang 1 đến `page-039.txt` tương ứng PDF trang 39). Người học đã đối chiếu PDF với TXT ở các trang 11, 27, 29, 33, 35, 37 và 39.

OCR chạy cục bộ bằng EasyOCR `vi+en`, Poppler, CPU, 260 DPI; hoàn tất 39/39 trang và ghi nhận 60.079 ký tự. Tệp OCR được giữ ngoài Git tại `data/processed/`; có thể tái tạo theo [quy trình OCR](../../docs/OCR-WORKFLOW.md). Nguồn, cách đếm trang và lưu ý quyền chia sẻ được ghi trong [manifest](../../data/manifest.json). Một số lỗi OCR vẫn còn; việc rà các trang trên không đồng nghĩa đã hiệu đính toàn bộ văn bản.

## 2. Benchmark và kiểm chứng evidence

Bộ benchmark có 20 câu, 15 dev và 5 test; sáu câu có filter theo chapter. Mỗi câu có đáp án tham chiếu, trang gold, evidence quote và filter nếu cần trong [questions.json](../../benchmark/questions.json). Tệp chương trình đã kiểm tra evidence quote có trong TXT gold sau khi chuẩn hóa khoảng trắng. Đây là kiểm tra dựa trên OCR; các câu hỏi số liệu/thời hạn cần được đọc cùng trang PDF gốc.

## 3. Pipeline và giả thuyết

Cả ba cấu hình dùng cùng corpus, model embedding `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` qua FastEmbed 0.7.3, Chroma PersistentClient 1.0.20 và cosine distance. FastEmbed cảnh báo model hiện dùng mean pooling; cảnh báo này được ghi lại và cùng implementation được dùng cho cả A/B/C.

- **A:** cửa sổ 650 ký tự, overlap 100. Giả thuyết ghi sau lần chạy: kích thước cố định dễ kiểm soát và overlap có thể giữ evidence cục bộ, nhưng ranh giới có thể cắt ngữ cảnh và làm tăng số chunk.
- **B:** nhóm dòng OCR liên tiếp, tối đa 1.400 ký tự. Giả thuyết ghi sau lần chạy: nhóm dòng có thể giữ thêm ngữ cảnh, giảm số chunk; lỗi OCR và nhóm quá rộng vẫn có thể làm giảm coherence.
- **C:** cùng chunking với B, thêm filter `chapter` khi câu hỏi có filter. Giả thuyết ghi sau lần chạy: filter có thể tăng tuân thủ phạm vi, nhưng không đảm bảo đoạn trả lời xuất hiện trong top-3.

Các giả thuyết được ghi lại sau khi đã xem kết quả, không phải giả thuyết đăng ký trước. Nhật ký đầy đủ tại [experiment_log.csv](../../artifacts/experiment_log.csv).

## 4. Kết quả retrieval

| Cấu hình | Chunks | Dev Hit@1 | Dev Evidence Hit@3 | Test Hit@1 | Test Evidence Hit@3 | Ingest (s) | Retrieval tổng (s) |
|---|---:|---:|---:|---:|---:|---:|---:|
| A — cửa sổ 650/100 | 122 | 5/15 | 6/15 | 2/5 | 2/5 | 6,935 | 0,452 |
| B — nhóm dòng OCR | 65 | 5/15 | 8/15 | 2/5 | 3/5 | 4,058 | 0,433 |
| C — B + filter chapter | 65 | 5/15 | 8/15 | 2/5 | 4/5 | 3,980 | 0,475 |

A có chunk 128–649 ký tự. B/C có chunk 5–1.399 ký tự; đoạn ngắn nhất là mảnh OCR rất ngắn. Tổng thời gian chạy được ghi là 17,192 giây; chi phí dịch vụ là 0 USD.

## 5. Coherence, metadata và grounding

Phiếu [manual-review-template.csv](../manual-review-template.csv) có 10 vị trí nguồn giống nhau cho từng cấu hình (30 nhãn coherence) và 5 câu test cho mỗi cấu hình (15 nhóm metadata/grounding). Phiếu hiển thị chủ đề, nội dung chunk, câu hỏi, đáp án tham chiếu, evidence và top-3 trace để có thể đối chiếu trực tiếp.

Các nhãn sau là đánh giá định tính do Codex (AI) thực hiện theo thang trong GUIDE, không phải đánh giá độc lập do người học chấm. Coherence: 0 = khó hiểu/bị cắt ý; 1 = hiểu một phần/thiếu ngữ cảnh; 2 = tự hiểu và giữ trọn ý. Grounding: 0 = top-3 không có bằng chứng; 1 = evidence thiếu điều kiện/ngữ cảnh; 2 = đủ evidence để trả lời và truy nguồn. Metadata được tính đủ/đúng khi `source`, `document_id`, `page` và `chapter` có mặt, nhất quán với trace và mapping trang. Filter compliance được tính khi cả ba hit trong top-3 thuộc chapter yêu cầu.

| Cấu hình | Coherence TB /2 (10 vị trí) | Metadata đủ/đúng (15 hit) | Tuân thủ filter (3 câu test) | Grounding TB /2 (5 câu test) | Phân bố grounding 0/1/2 |
|---|---:|---:|---:|---:|---|
| A | 1,0 | 15/15 | 0/3 | 0,8 | 3 / 0 / 2 |
| B | 1,2 | 15/15 | 2/3 | 1,2 | 2 / 0 / 3 |
| C | 1,2 | 15/15 | 3/3 | 1,6 | 1 / 0 / 4 |

Ví dụ lỗi: q16, C lọc đúng Chương II nhưng top-3 không có evidence về hạn 60 ngày nên grounding = 0. Với q19, B/C lấy được đoạn yêu cầu xóa hoặc trả dữ liệu sau khi kết thúc xử lý; A không lấy được đoạn đó. Metadata đúng không tự đảm bảo evidence liên quan.

## 6. Phân tích và kết luận

Trên dev, B và C cùng đạt Evidence Hit@3 8/15, hơn A với 6/15; C có thêm khả năng giới hạn kết quả theo chapter. Trên các câu test có filter, cả top-3 của C tuân thủ filter ở 3/3 câu, so với B 2/3 và A 0/3. Nếu ưu tiên phạm vi metadata, C là lựa chọn phù hợp hơn trong thí nghiệm này; B cho chất lượng coherence tương đương C vì dùng cùng cách chunking.

Tập test chỉ có năm câu và đã được xem trong quá trình hoàn thiện, nên không còn là holdout độc lập. Chênh lệch test (C 4/5, B 3/5, A 2/5) chỉ mô tả lần chạy này, không chứng minh cấu hình C tốt hơn trên tài liệu khác. Không dùng test để tuyên bố kết quả tổng quát. Cả chunking theo dòng và OCR đều có thể tạo đoạn rời rạc hoặc thiếu từ; thời gian cũng phụ thuộc máy chạy.

## 7. AI hỗ trợ và cách kiểm tra

Codex hỗ trợ hiện thực/chỉnh sửa pipeline, chuẩn bị benchmark, đọc trace và soạn phân tích. Tôi đã chạy OCR/pipeline cục bộ và đối chiếu trực quan các trang 11, 27, 29, 33, 35, 37, 39 với PDF. Các số liệu trong báo cáo lấy từ metrics/trace đã lưu; các điểm định tính được ghi rõ là do AI chấm, không gán cho người học. Quy tắc dùng AI và không tạo nhãn giả nằm trong [RULES.md](../../RULES.md).

## Artifacts và cách chạy

- Metrics: [metrics.json](../../starter/results/metrics.json)
- Traces: [A](../../starter/results/traces_A.json), [B](../../starter/results/traces_B.json), [C](../../starter/results/traces_C.json)
- Benchmark: [questions.json](../../benchmark/questions.json)
- Từ thư mục `starter/`: `python -m src.run` (cần cài requirements và có OCR TXT trong `data/processed/`).
