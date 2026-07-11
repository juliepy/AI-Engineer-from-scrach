[English Version →](../../../../en/resources/openai-advanced/sops/) | [中文版本 →](../../../../zh/resources/openai-advanced/sops/)

# Thư viện SOP

Các quy trình vận hành chuẩn từng bước để thiết lập và vận hành harness.

## SOP Có sẵn

- [`layered-domain-architecture.md`](./layered-domain-architecture.md):
  thiết lập kiến trúc domain phân lớp để agent không vi phạm ranh giới
- [`encode-knowledge-into-repo.md`](./encode-knowledge-into-repo.md):
  di chuyển kiến thức ẩn từ chat, tài liệu và bộ nhớ vào các tệp cục bộ repo
- [`observability-feedback-loop.md`](./observability-feedback-loop.md):
  cung cấp cho agent log, metrics, trace và vòng lặp debug có thể lặp lại
- [`chrome-devtools-validation-loop.md`](./chrome-devtools-validation-loop.md):
  sử dụng tự động hóa browser và snapshot để xác minh hành vi UI cho đến khi sạch

## Cách Sử dụng Chúng

1. Chọn SOP phù hợp với điểm nghẽn hiện tại của bạn.
2. Sử dụng danh sách kiểm tra để thiết lập các artifact hoặc công cụ còn thiếu.
3. Mã hóa các quy tắc kết quả vào các tài liệu `repo-template/` đã sao chép của bạn.
4. Chuyển đổi các nhận xét review lặp đi lặp lại thành kiểm tra, script hoặc guardrail.

Những điều này không phải để được tuân theo mù quáng. Chúng được thiết kế để làm cho harness có thể đọc được, có thể thực thi và có thể lặp lại hơn.
