# Bản đồ Phương pháp

Bảng này ánh xạ các chế độ lỗi coding-agent chạy lâu phổ biến nhất sang artifact hoặc quy tắc vận hành thường sửa chúng đầu tiên.

| Chế độ lỗi | Trông như thế nào trong thực tế | Sửa chữa chính | Artifact hỗ trợ |
| --- | --- | --- | --- |
| Nhầm lẫn cold-start | Một phiên mới dành hầu hết thời gian để khám phá lại cài đặt và trạng thái | Biến kho lưu trữ thành hệ thống ghi chép | `claude-progress.md` |
| Phình phạm vi | Agent bắt đầu nhiều tính năng và không hoàn thành sạch cái nào | Giới hạn phạm vi active | `feature_list.json` |
| Hoàn thành sớm | Agent tuyên bố xong sau khi chỉnh sửa mã nhưng trước khi có bằng chứng có thể chạy | Ràng buộc hoàn thành với bằng chứng | `clean-state-checklist.md` |
| Khởi động dễ vỡ | Mỗi phiên học lại cách khởi động dự án | Chuẩn hóa cài đặt và xác minh | `init.sh` |
| Bàn giao yếu | Phiên tiếp theo không thể biết những gì đã được xác minh, bị hỏng, hoặc là tiếp theo | Kết thúc với bàn giao rõ ràng | `session-handoff.md` |
| Review chủ quan | Chất lượng review phụ thuộc vào sở thích hoặc trí nhớ | Tính điểm đầu ra bằng các hạng mục cố định | `evaluator-rubric.md` |

## Nguyên tắc Vận hành

Thêm artifact nhỏ nhất giải quyết trực tiếp chế độ lỗi đã quan sát. Tránh giải quyết mọi vấn đề độ tin cậy bằng cách đổ thêm văn bản vào một tệp hướng dẫn toàn cục.
