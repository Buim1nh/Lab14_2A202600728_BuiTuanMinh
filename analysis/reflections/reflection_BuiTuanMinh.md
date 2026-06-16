# Báo cáo Cá nhân (Individual Reflection)
Họ và tên: Bùi Tuấn Minh
MSSV: 2A202600728

## 1. Vai trò trong nhóm
Trong dự án này, em đã đảm nhận vai trò chính trong việc:
- Phát triển kịch bản tạo dữ liệu (Synthetic Data Generation) bằng API.
- Cài đặt và cấu hình Evaluator (Hit Rate, MRR) cũng như Multi-Judge LLM.
- Chạy benchmark và tổng hợp báo cáo Failure Analysis.

## 2. Những khó khăn gặp phải
- Việc đảm bảo LLM sinh ra đúng định dạng JSON cho 50 test cases đôi khi gặp lỗi (parser error). Đã khắc phục bằng cách chia lô (batching) và dự phòng (fallback).
- Cấu hình Multi-Judge đòi hỏi phải xử lý sự không đồng thuận giữa các kết quả trả về từ API.

## 3. Bài học rút ra
- Nhận thức rõ tầm quan trọng của việc có bộ dataset chất lượng (Golden Dataset) trước khi đưa Agent vào ứng dụng thực tế.
- Đánh giá bằng LLM (LLM-as-a-judge) rất linh hoạt nhưng cần phải có calibration và chạy nhiều lượt để đảm bảo độ tin cậy.
