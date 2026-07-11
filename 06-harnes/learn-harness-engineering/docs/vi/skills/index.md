# Kỹ năng (Skills)

Thư mục này chứa các bộ kỹ năng (skills) đi kèm với khóa học này. Các kỹ năng là các mẫu prompt độc lập có thể được nạp bởi các AI coding agent (Claude Code, Codex, Cursor, Windsurf, v.v.) để thực hiện các tác vụ chuyên môn.

## harness-creator

Một kỹ năng xây dựng harness cấp độ thực tế (production-grade) dành cho AI coding agent. Nó giúp bạn tạo ra, đánh giá và cải thiện năm hệ thống cốt lõi của harness: hướng dẫn (instructions), trạng thái (state), xác minh (verification), phạm vi (scope) và vòng đời phiên làm việc (session lifecycle).

### Chức năng

- **Tạo harness từ đầu** — AGENTS.md, danh sách tính năng, luồng công việc xác minh
- **Cải thiện các harness hiện có** — Đánh giá năm hệ thống phụ với các cải tiến được ưu tiên
- **Thiết kế tính liên tục của phiên** — Lưu trữ bộ nhớ, theo dõi tiến độ, thủ tục bàn giao
- **Áp dụng các mẫu production** — Bộ nhớ, kỹ thuật ngữ cảnh, an toàn công cụ, điều phối đa agent

### Bắt đầu Nhanh

Các tệp kỹ năng nằm trong kho lưu trữ tại [`skills/harness-creator/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/skills/harness-creator).

```bash
npx skills add walkinglabs/learn-harness-engineering --skill harness-creator
```

Để sử dụng nó với Claude Code, hãy sao chép thư mục `harness-creator/` vào đường dẫn kỹ năng trong dự án của bạn, hoặc chỉ định tệp SKILL.md cho agent của bạn.

### Các Mẫu Tham Khảo (Reference Patterns)

Kỹ năng này bao gồm 7 tài liệu tham khảo tập trung:

| Mẫu (Pattern) | Khi nào sử dụng |
|---------|-------------|
| Lưu trữ bộ nhớ | Agent quên giữa các phiên |
| Skill Runtime | Đóng gói workflow tái sử dụng thành skill |
| Kỹ thuật ngữ cảnh | Quản lý ngân sách ngữ cảnh, nạp tức thời (JIT) |
| Đăng ký công cụ | An toàn công cụ, kiểm soát đồng thời |
| Điều phối Đa Agent | Xử lý song song, quy trình làm việc chuyên môn hóa |
| Vòng đời & Khởi động | Hooks, tác vụ nền, khởi tạo |
| Cạm bẫy (Gotchas) | 15 chế độ lỗi không rõ ràng kèm theo cách sửa |

### Các Mẫu (Templates)

Kỹ năng này đi kèm với các mẫu sẵn sàng sử dụng:

- `agents.md` — Khung AGENTS.md với các quy tắc hoạt động
- `feature-list.json` — JSON Schema + danh sách tính năng mẫu
- `init.sh` — Kịch bản khởi tạo tiêu chuẩn
- `progress.md` — Mẫu nhật ký tiến độ phiên làm việc
- `session-handoff.md` — Mẫu bàn giao phiên

### Scripts

Kỹ năng này cũng bao gồm các script Node.js thuần cho scaffold, xác thực, báo cáo đánh giá HTML và báo cáo benchmark cấu trúc.

### Kỹ năng này được Xây dựng như thế nào

`harness-creator` được phát triển bằng phương pháp **skill-creator** — kỹ năng meta (meta-skill) chính thức của Anthropic để tạo, thử nghiệm và cải thiện lặp đi lặp lại các kỹ năng của agent. skill-creator cung cấp một luồng công việc có cấu trúc (bản nháp → thử nghiệm → đánh giá → lặp lại) được tích hợp sẵn các công cụ chạy đánh giá (eval runners), máy chấm điểm (graders) và trình xem điểm chuẩn (benchmark viewer).

- **Mã nguồn skill-creator**: [anthropics/skills — skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator)
- **Tài liệu kỹ năng Claude Code**: [anthropics/claude-code — plugin-dev/skills](https://github.com/anthropics/claude-code/tree/main/plugins/plugin-dev/skills)
