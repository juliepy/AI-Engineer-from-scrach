[English Version →](../../../en/projects/project-06-runtime-observability-and-debugging/) | [中文版本 →](../../../zh/projects/project-06-runtime-observability-and-debugging/)

> Bài giảng liên quan: [Bài 11. Làm cho runtime của agent có thể quan sát được](./../../lectures/lecture-11-why-observability-belongs-inside-the-harness/index.md) · [Bài 12. Bàn giao sạch sẽ ở cuối mỗi phiên](./../../lectures/lecture-12-why-every-session-must-leave-a-clean-state/index.md)
> Tệp mẫu: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/vi/resources/templates/)

# Dự án 06. Xây dựng Harness Agent Đầy đủ (Capstone)

## Bạn Làm Gì

Đây là dự án capstone. Tập hợp tất cả những gì đã học trong năm dự án đầu tiên, chạy một benchmark đầy đủ, sau đó thực hiện một lần dọn dẹp để xác minh chất lượng có thể duy trì được.

Sử dụng một bộ tác vụ đa tính năng cố định bao phủ toàn bộ product slice: import tài liệu, indexing, Q&A dựa trên trích dẫn, observability runtime, và trạng thái repo có thể đọc và khởi động lại. Lần đầu chạy với baseline harness yếu, sau đó với harness mạnh nhất của bạn, sau đó dọn dẹp và chạy lại. Cuối cùng, thực hiện thí nghiệm ablation harness — xóa từng thành phần một và xem cái nào thực sự quan trọng.

## Dùng project có sẵn trong repo

Đường dẫn repo: [`projects/project-06/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-06)

| Thư mục | Nội dung | So sánh gì |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-06/starter) | Sản phẩm gần như hoàn chỉnh, nhưng harness bị cố ý làm yếu: chỉ có [`AGENTS.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/starter/AGENTS.md) cơ bản, không có `feature_list.json`, `session-handoff.md`, clean-state checklist hay benchmark/cleanup scripts. | Ghi nhận thủ công baseline với harness yếu. |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-06/solution) | Harness đầy đủ: [`AGENTS.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/AGENTS.md), [`CLAUDE.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/CLAUDE.md), [`feature_list.json`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/feature_list.json), [`init.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/init.sh), [`session-handoff.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/session-handoff.md), [`clean-state-checklist.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/clean-state-checklist.md), tài liệu chất lượng/đánh giá và scripts. | Chạy [`projects/project-06/solution/scripts/benchmark.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/scripts/benchmark.sh) và [`projects/project-06/solution/scripts/cleanup-scanner.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/scripts/cleanup-scanner.sh), rồi so sánh bằng chứng chất lượng. |

## Công cụ

- Claude Code hoặc Codex
- Git
- Node.js + Electron
- Mẫu tài liệu chất lượng
- Rubric evaluator
- Tất cả các thành phần harness tích lũy từ năm dự án đầu tiên

## Cơ chế Harness

Harness đầy đủ: tất cả các cơ chế + observability + nghiên cứu ablation
