# AGENTS.md

Kho lưu trữ này được thiết kế cho công việc coding-agent chạy lâu. Mục tiêu không phải là tối đa hóa đầu ra mã thô. Mục tiêu là để lại repo ở trạng thái mà phiên tiếp theo có thể tiếp tục mà không cần đoán.

## Quy trình Khởi động

Trước khi viết mã:

1. Xác nhận thư mục làm việc bằng `pwd`.
2. Đọc `claude-progress.md` để biết trạng thái đã xác minh mới nhất và bước tiếp theo.
3. Đọc `feature_list.json` và chọn tính năng chưa hoàn thành có mức ưu tiên cao nhất.
4. Xem lại các commit gần đây bằng `git log --oneline -5`.
5. Chạy `./init.sh`.
6. Chạy xác minh smoke hoặc end-to-end cần thiết trước khi bắt đầu công việc mới.

Nếu xác minh baseline đã thất bại, hãy sửa điều đó trước. Không chồng công việc tính năng mới lên trên trạng thái khởi đầu bị hỏng.

## Quy tắc Làm việc

- Làm việc trên một tính năng tại một thời điểm.
- Không đánh dấu tính năng hoàn thành chỉ vì mã đã được thêm vào.
- Giữ các thay đổi trong phạm vi tính năng đã chọn trừ khi có sự cố chặn cần sửa hỗ trợ hẹp.
- Không thay đổi ngầm các quy tắc xác minh trong khi triển khai.
- Ưu tiên các artifact repo lâu bền hơn tóm tắt chat.

## Artifact Bắt buộc

- `feature_list.json`: nguồn sự thật cho trạng thái tính năng
- `claude-progress.md`: nhật ký phiên và trạng thái đã xác minh hiện tại
- `init.sh`: đường dẫn khởi động và xác minh chuẩn
- `session-handoff.md`: bàn giao ngắn gọn tùy chọn cho các phiên lớn hơn

## Định nghĩa Hoàn thành

Một tính năng chỉ xong khi tất cả những điều sau đây là đúng:

- hành vi mục tiêu đã được triển khai
- xác minh cần thiết đã thực sự chạy
- bằng chứng được ghi lại trong `feature_list.json` hoặc `claude-progress.md`
- kho lưu trữ vẫn có thể khởi động lại từ đường dẫn khởi động chuẩn

## Cuối Phiên

Trước khi kết thúc phiên:

1. Cập nhật `claude-progress.md`.
2. Cập nhật `feature_list.json`.
3. Ghi lại bất kỳ rủi ro hoặc sự cố chặn chưa được giải quyết nào.
4. Commit với thông điệp mô tả khi công việc ở trạng thái an toàn.
5. Để repo đủ sạch để phiên tiếp theo có thể chạy `./init.sh` ngay lập tức.
