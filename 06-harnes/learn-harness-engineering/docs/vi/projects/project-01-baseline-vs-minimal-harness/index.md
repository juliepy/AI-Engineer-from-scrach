[English Version →](../../../en/projects/project-01-baseline-vs-minimal-harness/) | [中文版本 →](../../../zh/projects/project-01-baseline-vs-minimal-harness/)

> Bài giảng liên quan: [Bài 01. Mô hình mạnh không có nghĩa là thực thi đáng tin cậy](./../../lectures/lecture-01-why-capable-agents-still-fail/index.md) · [Bài 02. Harness thực sự có nghĩa là gì](./../../lectures/lecture-02-what-a-harness-actually-is/index.md)
> Tệp mẫu: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/vi/resources/templates/)

# Dự án 01. Chỉ Prompt vs. Ưu tiên Quy tắc: Sự Khác biệt Lớn thế Nào

## Bạn Làm Gì

Xây dựng một ứng dụng Electron knowledge-base shell tối giản — một cửa sổ với danh sách tài liệu bên trái, panel Q&A bên phải, và thư mục dữ liệu cục bộ. Bản thân tác vụ không phức tạp. Điều phức tạp là cách bạn để agent hoàn thành nó.

Bạn chạy hai lần. Lần đầu: chỉ một prompt, không chuẩn bị gì. Lần hai: `AGENTS.md`, `init.sh`, `feature_list.json` được đặt sẵn trong repo. Sau đó so sánh.

Kịch bản của bài học này dùng một khoảng tái khám phá/chuẩn bị ngắn làm ví dụ, không phải kết quả đo cố định.

## Công cụ

- Claude Code hoặc Codex (chọn một, sử dụng cho cả hai lần chạy)
- Git (quản lý branch và so sánh)
- Node.js + Electron (tech stack dự án)
- Đồng hồ đo thời gian (ghi lại thời gian mỗi lần chạy)

## Cơ chế Harness

Harness tối giản: `AGENTS.md` + `init.sh` + `feature_list.json`

## Dùng project đã có sẵn trong repo

Đường dẫn trong repo: [`projects/project-01/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-01)

| Thư mục | Có gì bên trong | Cách dùng / so sánh |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-01/starter) | Lượt chạy harness yếu. Chỉ có [`task-prompt.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/starter/task-prompt.md) làm mô tả nhiệm vụ, không có `AGENTS.md` hay `feature_list.json`. | Đưa prompt cho agent và đo xem nó hoàn thành được gì khi không có cấu trúc bổ sung. |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-01/solution) | Cùng slice sản phẩm nhưng có artefact harness rõ ràng: [`AGENTS.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/AGENTS.md), [`CLAUDE.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/CLAUDE.md), [`init.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/init.sh), [`feature_list.json`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/feature_list.json), [`claude-progress.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/claude-progress.md). | So sánh cách quy tắc và kiểm chứng biến cùng nhiệm vụ thành thứ có thể chạy và kiểm tra được. |

Bốn tính năng cụ thể là: mở cửa sổ, danh sách tài liệu, panel câu hỏi, và tạo thư mục dữ liệu cục bộ. Xem `solution/feature_list.json` để biết bằng chứng mong đợi cho từng tính năng.
