[English Version →](../../../en/projects/project-04-incremental-indexing/) | [中文版本 →](../../../zh/projects/project-04-incremental-indexing/)

> Bài giảng liên quan: [Bài 07. Vạch ranh giới tác vụ rõ ràng cho agent](./../../lectures/lecture-07-why-agents-overreach-and-under-finish/index.md) · [Bài 08. Sử dụng feature list để ràng buộc những gì agent làm](./../../lectures/lecture-08-why-feature-lists-are-harness-primitives/index.md)
> Tệp mẫu: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/vi/resources/templates/)

# Dự án 04. Sử dụng Phản hồi Runtime để Điều chỉnh Hành vi Agent

## Bạn Làm Gì

Thêm observability runtime (log khởi động, log import/indexing, trạng thái lỗi) và các ràng buộc kiến trúc để ngăn chặn vi phạm xuyên lớp. Cài một lỗi runtime để agent sửa.

Bạn chạy hai lần: lần đầu không có log hoặc ràng buộc, lần hai với các công cụ và quy tắc phù hợp.

## Dùng project có sẵn trong repo

Đường dẫn repo: [`projects/project-04/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-04)

| Thư mục | Nội dung | So sánh gì |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-04/starter) | Code Project 03 với tín hiệu chẩn đoán yếu. Lỗi indexing được cài sẵn có thể làm hỏng chunking file lớn, và không có script kiểm tra kiến trúc. | Agent mất bao lâu để tìm root cause khi thiếu runtime signals. |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-04/solution) | Structured logger, tài liệu/script ranh giới kiến trúc, logic chunking đã sửa và [`clean-state-checklist.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/clean-state-checklist.md). | Logs và boundary checks có giúp sửa nhanh hơn, ít xâm lấn hơn không. |

File cần xem: [`projects/project-04/solution/src/services/logger.ts`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/src/services/logger.ts), [`projects/project-04/solution/scripts/check-architecture.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/scripts/check-architecture.sh), [`projects/project-04/solution/docs/ARCHITECTURE.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/docs/ARCHITECTURE.md), [`projects/project-04/solution/src/services/indexing-service.ts`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/src/services/indexing-service.ts).

## Công cụ

- Claude Code hoặc Codex
- Git
- Node.js + Electron

## Cơ chế Harness

Phản hồi runtime + kiểm soát phạm vi + indexing tăng dần
