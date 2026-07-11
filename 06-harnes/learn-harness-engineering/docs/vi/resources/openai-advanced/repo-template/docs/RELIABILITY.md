# RELIABILITY.md

Tệp này định nghĩa cách hệ thống chứng minh nó khỏe mạnh và có thể khởi động lại.

## Đường dẫn Chuẩn

- Bootstrap: `[lệnh]`
- Xác minh: `[lệnh]`
- Khởi động app hoặc service: `[lệnh]`
- Debug hoặc kiểm tra runtime: `[lệnh]`

## Tín hiệu Runtime Bắt buộc

- log có cấu trúc cho khởi động và các luồng quan trọng
- health check cho các service chính
- dữ liệu trace hoặc timing cho các đường dẫn chậm khi có sẵn
- trạng thái lỗi có thể nhìn thấy của người dùng cho các thất bại có thể phục hồi

## Journey Vàng

- `[journey 1]`
- `[journey 2]`
- `[journey 3]`

Mỗi journey vàng nên có đường dẫn xác minh có thể lặp lại và tín hiệu thất bại rõ ràng.

## Quy tắc Độ tin cậy

- Không có tính năng nào hoàn thành nếu hệ thống không thể khởi động lại sạch sẽ sau đó.
- Các thất bại runtime nên có thể chẩn đoán từ các tín hiệu cục bộ repo.
- Nếu một chế độ thất bại lặp đi lặp lại xuất hiện, hãy thêm benchmark hoặc guardrail cho nó.
- Dọn dẹp là một phần của độ tin cậy, không phải một mối quan tâm riêng biệt.
