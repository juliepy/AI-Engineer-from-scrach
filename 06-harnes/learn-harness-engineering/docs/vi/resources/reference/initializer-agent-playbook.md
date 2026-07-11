# Playbook Initializer Agent

Sử dụng playbook này cho phiên nghiêm túc đầu tiên trong một kho lưu trữ, trước khi công việc tính năng tăng dần bắt đầu.

## Mục tiêu

Tạo ra một bề mặt vận hành ổn định để các phiên sau có thể triển khai hành vi mà không cần phải suy ra lại các lệnh khởi động, trạng thái hiện tại, hoặc ranh giới tác vụ.

## Kết quả Đầu ra Bắt buộc

Initializer nên để lại ít nhất các artifact này:

- một tệp hướng dẫn gốc như `AGENTS.md` hoặc `CLAUDE.md`
- một bề mặt tính năng có thể đọc bởi máy như `feature_list.json`
- một artifact tiến độ lâu bền như `claude-progress.md`
- một helper khởi động chuẩn như `init.sh`
- một commit cơ sở an toàn ban đầu ghi lại scaffold cơ sở

## Danh sách Kiểm tra

1. Định nghĩa đường dẫn khởi động chuẩn.
2. Định nghĩa đường dẫn xác minh chuẩn.
3. Tạo nhật ký tiến độ và ghi lại trạng thái khởi đầu.
4. Phân chia công việc thành các tính năng rõ ràng với trạng thái.
5. Tạo commit baseline sạch đầu tiên.

## Bài kiểm tra Thành công

Một phiên mới không có ngữ cảnh chat trước đó nên có thể trả lời:

- kho lưu trữ này làm gì
- cách khởi động nó
- cách xác minh nó
- những gì chưa hoàn thành
- bước tốt nhất tiếp theo là gì
