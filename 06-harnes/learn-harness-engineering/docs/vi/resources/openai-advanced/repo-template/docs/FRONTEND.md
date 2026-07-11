# FRONTEND.md

Tệp này định nghĩa các kỳ vọng frontend ổn định để agent không phát minh ra các mẫu UI một cách không thể đoán trước.

## Nguyên tắc UI

- Tối ưu hóa cho sự rõ ràng trước sự mới lạ.
- Giữ các luồng tương tác có thể khám phá và khởi động lại được.
- Ưu tiên một số ít component tái sử dụng thay vì các biến thể một lần.
- Kiểm tra accessibility là một phần của xác minh thông thường, không phải công việc đánh bóng.

## Guardrail

- Ghi lại design system hoặc thư viện component trong `docs/references/`.
- Ghi lại các trạng thái quan trọng dành cho người dùng: trống, đang tải, thành công, lỗi, thử lại.
- Giữ copy, hành vi bàn phím và hệ thống phân cấp trực quan nhất quán qua các luồng.
- Khi một lỗi UI được sửa, hãy thêm hoặc cập nhật bước xác minh phù hợp.

## Kỳ vọng Xác minh

- Ghi lại bằng chứng cho các user journey quan trọng.
- Ghi lại các bước xác minh browser hoặc runtime trong kế hoạch liên quan.
- Nếu các hồi quy trực quan phổ biến, hãy chuẩn hóa kiểm tra screenshot hoặc DOM.
