[English Version →](../../../en/projects/project-05-grounded-qa-verification/) | [中文版本 →](../../../zh/projects/project-05-grounded-qa-verification/)

> Bài giảng liên quan: [Bài 09. Ngăn agent tuyên bố hoàn thành quá sớm](./../../lectures/lecture-09-why-agents-declare-victory-too-early/index.md) · [Bài 10. Chỉ testing end-to-end mới là xác minh thực sự](./../../lectures/lecture-10-why-end-to-end-testing-changes-results/index.md)
> Tệp mẫu: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/vi/resources/templates/)

# Dự án 05. Để Agent Xác minh Công việc của Chính nó

## Bạn Làm Gì

Triển khai phân tách vai trò — một generator thực hiện, một evaluator review, và tùy chọn một planner. Chạy ba lần để đo lường tác động của mỗi vai trò được thêm vào.

Chọn một tính năng nâng cấp thực chất (hội thoại đa lượt, thiết kế lại citation panel, hoặc lọc tài liệu) và giữ nó nhất quán qua tất cả các lần chạy.

## Dùng project có sẵn trong repo

Đường dẫn repo: [`projects/project-05/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05)

| Thư mục | Nội dung | So sánh gì |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/starter) | Ứng dụng dựa trên Project 04 trước khi nâng cấp lịch sử hội thoại. | Điểm bắt đầu nếu muốn chạy lại ba biến thể. |
| [`solution/single-role/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/solution/single-role) | Một agent tự lập kế hoạch, triển khai và tự đánh giá. | Điểm số và lỗi trong [`evaluator-rubric.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/single-role/evaluator-rubric.md). |
| [`solution/gen-eval/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/solution/gen-eval) | Generator + evaluator, có bằng chứng sửa đổi. | Điểm số và revision notes trong [`evaluator-rubric.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/gen-eval/evaluator-rubric.md). |
| [`solution/plan-gen-eval/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/solution/plan-gen-eval) | Planner + generator + evaluator với sprint contract. | [`sprint-contract.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/plan-gen-eval/sprint-contract.md) và bằng chứng điểm cao hơn trong [`evaluator-rubric.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/plan-gen-eval/evaluator-rubric.md). |

## Công cụ

- Claude Code hoặc Codex
- Git
- Node.js + Electron

## Cơ chế Harness

Tự xác minh + Q&A có grounding + hoàn thành dựa trên bằng chứng
