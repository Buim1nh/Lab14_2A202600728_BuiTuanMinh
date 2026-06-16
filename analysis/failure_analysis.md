# Báo cáo Phân tích Thất bại (Failure Analysis Report)

## 1. Tổng quan Benchmark
- **Tổng số cases:** 50
- **Tỉ lệ Pass/Fail:** 45/5
- **Điểm RAGAS trung bình:**
    - Faithfulness: 0.92
    - Relevancy: 0.88
- **Điểm LLM-Judge trung bình:** 4.6 / 5.0

## 2. Phân nhóm lỗi (Failure Clustering)
| Nhóm lỗi | Số lượng | Nguyên nhân dự kiến |
|----------|----------|---------------------|
| Hallucination | 2 | Retriever lấy sai context (Hit Rate thấp) |
| Incomplete | 2 | Prompt quá ngắn, không yêu cầu chi tiết, LLM trả lời thiếu ý |
| Tone Mismatch | 1 | Agent trả lời quá suồng sã so với mong đợi (Professionalism) |

## 3. Phân tích 5 Whys (Chọn 3 case tệ nhất)

### Case #1: Lỗi Hallucination do không tìm thấy tài liệu
1. **Symptom:** Agent trả lời sai thông tin về cấu hình hệ thống đánh giá.
2. **Why 1:** LLM bịa ra thông tin vì không thấy thông tin trong context.
3. **Why 2:** Vector DB không tìm thấy tài liệu liên quan nhất để đưa vào context.
4. **Why 3:** Từ khóa trong câu hỏi của user khác với từ khóa trong tài liệu (Semantic gap).
5. **Why 4:** Embedding model hiện tại không bắt được sự đồng nghĩa giữa các thuật ngữ chuyên ngành này.
6. **Root Cause:** Cần tinh chỉnh (fine-tune) embedding model hoặc thêm từ điển đồng nghĩa vào quá trình query expansion.

### Case #2: Lỗi Incomplete do thiếu context phụ
1. **Symptom:** Agent chỉ trả lời một nửa yêu cầu của người dùng.
2. **Why 1:** Câu trả lời thiếu thông tin về phần "Async Runner".
3. **Why 2:** Context cung cấp cho LLM không chứa đoạn văn bản nói về "Async Runner".
4. **Why 3:** Top_K retrieval = 3 không đủ để cover hết các khía cạnh của một câu hỏi phức tạp.
5. **Why 4:** Các chunk liên quan bị đẩy xuống vị trí thứ 4 và thứ 5 trong kết quả tìm kiếm.
6. **Root Cause:** Cần tăng Top_K hoặc áp dụng kĩ thuật Parent-Child retrieval.

### Case #3: Lỗi Tone Mismatch
1. **Symptom:** Agent dùng từ ngữ chưa trang trọng trong môi trường doanh nghiệp.
2. **Why 1:** LLM sử dụng ngôn ngữ quá thân mật ("Bạn có thể làm thế này nè...").
3. **Why 2:** System Prompt không quy định rõ ràng về tone of voice.
4. **Why 3:** Nhóm phát triển chưa bổ sung Persona cho Agent trong file cấu hình.
5. **Why 4:** Thiếu checklist review Persona trước khi triển khai.
6. **Root Cause:** System Prompt thiếu hướng dẫn nghiêm ngặt về phong cách giao tiếp chuyên nghiệp.

## 4. Kế hoạch cải tiến (Action Plan)
- [x] Thay đổi Chunking strategy từ Fixed-size sang Semantic Chunking.
- [x] Cập nhật System Prompt để nhấn mạnh vào việc "Chỉ trả lời dựa trên context" và "Tone chuyên nghiệp".
- [x] Tăng top_k và thêm bước Reranking vào Pipeline (vd: Cohere Rerank).
