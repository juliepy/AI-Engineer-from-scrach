# Luồng Khởi động Coding Agent

Sử dụng cái này ở đầu mỗi phiên sau khi khởi tạo hoàn thành.

## Mẫu Khởi động Cố định

1. Chạy `pwd` và xác nhận thư mục gốc kho lưu trữ.
2. Đọc `claude-progress.md`.
3. Đọc `feature_list.json`.
4. Xem lại các commit gần đây bằng `git log --oneline -5`.
5. Chạy `./init.sh`.
6. Chạy một đường dẫn smoke hoặc end-to-end baseline.
7. Nếu baseline bị hỏng, hãy sửa điều đó trước.
8. Chọn tính năng chưa hoàn thành có mức ưu tiên cao nhất.
9. Chỉ làm việc trên tính năng đó cho đến khi nó được xác minh hoặc bị chặn rõ ràng.

## Tại sao Thứ tự này Quan trọng

- `pwd` ngăn chặn việc vô tình làm việc trong thư mục sai.
- các tệp tiến độ và tính năng khôi phục trạng thái lâu bền trước khi bắt đầu chỉnh sửa mới.
- các commit gần đây giải thích những gì đã thay đổi gần đây nhất.
- `init.sh` chuẩn hóa khởi động thay vì dựa vào bộ nhớ.
- xác minh baseline bắt các trạng thái khởi đầu bị hỏng trước khi công việc mới che giấu chúng.

## Gương Cuối Phiên

Cùng một phiên nên kết thúc bằng cách:

1. ghi lại tiến độ
2. cập nhật trạng thái tính năng
3. viết bàn giao nếu cần
4. commit công việc an toàn
5. để lại đường dẫn khởi động lại sạch sẽ
