# CLAUDE.md

Bạn đang làm việc trong một kho lưu trữ được thiết kế cho công việc triển khai chạy lâu. Ưu tiên hoàn thành đáng tin cậy, tính liên tục qua các phiên, và xác minh rõ ràng hơn tốc độ.

## Vòng lặp Vận hành

Ở đầu mỗi phiên:

1. Chạy `pwd` và xác nhận bạn đang ở trong thư mục gốc kho lưu trữ dự kiến.
2. Đọc `claude-progress.md`.
3. Đọc `feature_list.json`.
4. Xem lại các commit gần đây bằng `git log --oneline -5`.
5. Chạy `./init.sh`.
6. Kiểm tra xem đường dẫn smoke hoặc end-to-end baseline có đã bị hỏng chưa.

Sau đó chọn chính xác một tính năng chưa hoàn thành và chỉ làm việc trên tính năng đó cho đến khi bạn xác minh nó hoặc ghi lại lý do tại sao nó bị chặn.

## Quy tắc

- Một tính năng active tại một thời điểm.
- Không tuyên bố hoàn thành mà không có bằng chứng có thể chạy được.
- Không viết lại feature list để ẩn công việc chưa hoàn thành.
- Không xóa hoặc làm yếu các test chỉ để tác vụ có vẻ hoàn thành.
- Sử dụng các artifact kho lưu trữ như hệ thống ghi chép.

## Tệp Bắt buộc

- `feature_list.json`
- `claude-progress.md`
- `init.sh`
- `session-handoff.md` khi bàn giao ngắn gọn hữu ích

## Cổng Hoàn thành

Một tính năng chỉ có thể chuyển sang `passing` sau khi xác minh cần thiết thành công và kết quả được ghi lại.

## Trước khi Bạn Dừng

1. Cập nhật nhật ký tiến độ.
2. Cập nhật trạng thái tính năng.
3. Ghi lại những gì vẫn bị hỏng hoặc chưa được xác minh.
4. Commit khi kho lưu trữ an toàn để tiếp tục.
5. Để lại đường dẫn khởi động lại sạch sẽ cho phiên tiếp theo.
