# Submission — bài cá nhân

## Repo bài nộp

Fork repo đề bài hoặc clone rồi đẩy lên repo cá nhân. Đặt tên gợi ý `K5-L3A-DAY06-MSSV-DataIngestion` hoặc `K5-L3B-DAY06-MSSV-DataIngestion`; theo hướng dẫn lớp nếu có quy ước khác. Điền [STUDENT.md](STUDENT.md) và nộp link repo theo kênh giảng viên/coach chỉ định. Thời hạn do giảng viên/coach thông báo.

## Cấu trúc tối thiểu

```text
STUDENT.md
README.md                         # cách setup, chạy, đường dẫn dữ liệu
src/ hoặc starter/src/             # code pipeline do học viên viết
data/manifest.*                   # nguồn, trang, quyền, cách lấy
benchmark/                        # câu hỏi, split, gold evidence
artifacts/experiment_log.csv      # cấu hình và giả thuyết A/B/C
results/                          # thống kê, trace, nhãn audit, log
report/individual/<MSSV>_<HoTen>.md
```

Mẫu báo cáo: [report/individual/MSSV_HoTen.md](report/individual/MSSV_HoTen.md). `src/` có thể đặt ở root hoặc `starter/src/`; benchmark và dữ liệu thật do học viên tạo. Nếu không được phép nộp dữ liệu gốc hoặc trace chứa nội dung bị hạn chế, cung cấp hướng dẫn truy cập/tái tạo và minh chứng được phép chia sẻ; báo cho người chấm biết cách xác minh.

## Checklist

- [x] Dữ liệu 39 trang vật lý; manifest ghi nguồn, quyền, số trang và quy tắc tính. OCR giữ ngoài Git; phạm vi bao gồm trang mở đầu và biểu mẫu phụ lục.
- [x] Có 20 câu benchmark (15 dev / 5 test), evidence và trang nguồn; học viên xác nhận đã kiểm tra evidence. Lưu ý: tập test đã được xem trong lúc hoàn thiện nên không còn là holdout độc lập.
- [x] Có embedding model thật và Chroma PersistentClient hỗ trợ lưu bền vững, vector search, metadata filter; phiên bản và cấu hình được ghi trong báo cáo/metrics.
- [x] Có ba cấu hình A/B/C trên cùng model, corpus và benchmark; B–C so sánh tác động của filter chapter.
- [x] Đã chạy và lưu trace top-3, chỉ số dev/test, thời gian và chi phí trong `starter/results/`.
- [x] Có phiếu audit và phân tích coherence, metadata, grounding cùng retrieval/chunking; các nhãn định tính được ghi rõ là AI hỗ trợ, không phải đánh giá độc lập của học viên.
- [x] Có lệnh chạy, code, manifest, experiment log và báo cáo cá nhân.
- [x] Rà soát repo hiện tại: không thấy secret, dữ liệu cá nhân hoặc OCR corpus cục bộ; ảnh PDF tạm đã được xóa. Cần tiếp tục giữ nguyên lưu ý quyền chia sẻ trong manifest.
- [x] Repo đã đẩy lên GitHub và `main` đồng bộ với `origin/main` tại lần rà soát gần nhất.
