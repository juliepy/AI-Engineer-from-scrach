# Ví dụ: Biến Phản hồi Review thành Quy tắc

Nhận xét review lặp đi lặp lại:

> Không gọi filesystem utilities từ renderer. Sử dụng preload bridge.

Quy tắc harness được đẩy lên:

- thêm lint hoặc quy tắc import ngăn việc sử dụng `fs` trong mã renderer
- thêm văn bản giải pháp giải thích ranh giới preload
