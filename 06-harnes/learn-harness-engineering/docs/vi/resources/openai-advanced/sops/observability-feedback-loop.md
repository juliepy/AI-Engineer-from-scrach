# SOP: Vòng lặp Phản hồi Observability

Sử dụng SOP này khi debug chậm, agent tiếp tục tuyên bố thành công mà không có bằng chứng, hoặc hành vi runtime khó kiểm tra hơn bản thân mã.

## Mục tiêu

Cung cấp cho agent một vòng lặp phản hồi cục bộ qua log, metrics, trace và workload có thể chạy để nó có thể lý luận từ thực thi, không chỉ từ kiểm tra mã.

## Stack Tối thiểu

- ứng dụng phát ra các log có cấu trúc
- ứng dụng phát ra metrics và trace khi khả thi
- lớp fan-out hoặc thu thập cục bộ
- giao diện truy vấn cho log, metrics và trace
- workload hoặc user journey có thể lặp lại để chạy lại sau mỗi thay đổi

## SOP Thực thi

1. Định nghĩa các journey runtime vàng quan trọng nhất.
2. Thêm các log có cấu trúc vào khởi động và đường dẫn quan trọng.
3. Thêm metrics cho độ trễ, số lần thất bại hoặc độ sâu hàng đợi khi hữu ích.
4. Thêm trace hoặc marker timing cho các luồng chậm hoặc nhiều bước.
5. Làm cho các tín hiệu có thể truy vấn từ môi trường dev cục bộ.
6. Cung cấp cho agent một workload hoặc kịch bản có thể lặp lại để chạy lại.
7. Yêu cầu vòng lặp: truy vấn -> tương quan -> lý luận -> triển khai -> khởi động lại -> chạy lại -> xác minh.

## Danh sách Kiểm tra Phiên Debug

- Điều gì đã thất bại?
- Tín hiệu nào chứng minh sự thất bại?
- Lớp nào sở hữu sự thất bại?
- Điều gì thay đổi sau khi sửa?
- Ứng dụng có khởi động lại sạch sẽ không?
- Cùng workload có vượt qua sau khi chạy lại không?

## Định nghĩa Hoàn thành

- Agent có thể giải thích một chế độ thất bại từ bằng chứng runtime.
- Cùng workload có thể được chạy lại sau mỗi thay đổi.
- Khởi động lại và chạy lại là một phần của vòng lặp tác vụ bình thường.
- Các tín hiệu độ tin cậy được ghi lại trong `docs/RELIABILITY.md`.
