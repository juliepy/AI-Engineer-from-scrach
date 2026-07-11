# Ví dụ Các Thành phần Harness

Đối với một coding agent làm việc trong kho lưu trữ cục bộ:

- Mô hình:
  bản thân LLM

- Harness:
  - system prompt
  - AGENTS.md
  - bash tool
  - công cụ đọc/ghi tệp
  - quyền truy cập git
  - hệ thống tệp cục bộ
  - script khởi động
  - lệnh test
  - stop hook
  - kiểm tra lint
  - vòng lặp evaluator

Nếu bạn thay đổi bất kỳ phần harness nào ở trên, bạn thay đổi agent thực tế.
