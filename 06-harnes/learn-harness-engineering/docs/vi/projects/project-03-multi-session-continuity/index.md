[English Version →](../../../en/projects/project-03-multi-session-continuity/) | [中文版本 →](../../../zh/projects/project-03-multi-session-continuity/)

> Bài giảng liên quan: [Bài 05. Duy trì ngữ cảnh qua các phiên](./../../lectures/lecture-05-why-long-running-tasks-lose-continuity/index.md) · [Bài 06. Khởi tạo trước mỗi phiên agent](./../../lectures/lecture-06-why-initialization-needs-its-own-phase/index.md)
> Tệp mẫu: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/vi/resources/templates/)

# Dự án 03. Giữ cho Agent Tiếp tục Làm việc Qua Các Lần Khởi động Lại Phiên

## Bạn Làm Gì

Thêm kiểm soát phạm vi và cổng xác minh vào agent. Triển khai document chunking, metadata extraction, hiển thị tiến độ indexing, và luồng Q&A dựa trên trích dẫn. Sử dụng `feature_list.json` để theo dõi trạng thái tính năng — mỗi lần một tính năng, không đánh dấu là "pass" mà không có bằng chứng xác minh.

Bạn chạy hai lần: lần đầu không có ràng buộc, lần hai với thực thi nghiêm ngặt.

## Dùng project có sẵn trong repo

Đường dẫn repo: [`projects/project-03/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-03)

| Thư mục | Nội dung | So sánh gì |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-03/starter) | Code Project 02 với indexing và Q&A có citation vẫn chưa hoàn chỉnh. Có [`feature_list.json`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/starter/feature_list.json) ban đầu nhưng chưa có artefact handoff/restart cuối cùng. | Agent có drift qua nhiều tính năng hoặc mất trạng thái sau restart không. |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-03/solution) | Chunking, metadata, index status và citation-based QA đã hoàn thành, thêm [`init.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/init.sh), [`session-handoff.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/session-handoff.md), [`claude-progress.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/claude-progress.md), [`clean-state-checklist.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/clean-state-checklist.md). | Mỗi tính năng có bằng chứng kiểm chứng trước khi đánh dấu pass không. |

## Công cụ

- Claude Code hoặc Codex
- Git
- Node.js + Electron

## Cơ chế Harness

Nhật ký tiến độ + bàn giao phiên + tính liên tục đa phiên
