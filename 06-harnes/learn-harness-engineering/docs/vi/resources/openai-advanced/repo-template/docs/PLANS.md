# PLANS.md

Tệp này định nghĩa cách các kế hoạch thực thi được tạo, cập nhật, hoàn thành và lưu trữ.

## Khi Cần Một Kế hoạch

Tạo một kế hoạch thực thi khi công việc:

- trải dài hơn một phiên
- thay đổi nhiều hơn một hệ thống con
- có rủi ro xác minh hoặc triển khai không tầm thường
- phụ thuộc vào các quyết định mở nên được ghi lại

## Vị trí Kế hoạch

- `docs/exec-plans/active/`: các kế hoạch hiện đang thúc đẩy công việc
- `docs/exec-plans/completed/`: các kế hoạch đã hoàn thành được giữ lại để cung cấp ngữ cảnh cho agent trong tương lai
- `docs/exec-plans/tech-debt-tracker.md`: công việc đã hoãn và các follow-up

## Các Phần Kế hoạch Tối thiểu

- mục tiêu
- phạm vi và ngoài phạm vi
- đường dẫn xác minh
- rủi ro và sự cố chặn
- nhật ký tiến độ
- quyết định mở

## Quy tắc Vận hành

- Một kế hoạch active nên có một bước hiện tại được sở hữu rõ ràng.
- Cập nhật kế hoạch khi công việc tiến triển; đừng coi nó như văn xuôi tĩnh.
- Nếu một quyết định thay đổi hướng triển khai, hãy ghi lại nó trong kế hoạch.
- Di chuyển các kế hoạch đã hoàn thành sang `completed/` để agent vẫn có thể khám phá ngữ cảnh trước đó.
