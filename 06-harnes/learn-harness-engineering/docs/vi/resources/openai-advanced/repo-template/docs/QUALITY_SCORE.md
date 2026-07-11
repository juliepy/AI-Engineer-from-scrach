# QUALITY_SCORE.md

Tài liệu này theo dõi liệu kho lưu trữ có đang trở nên mạnh hơn hay yếu hơn theo thời gian.

## Thang điểm

- `A`: đã xác minh, có thể đọc được, ổn định, ranh giới được thực thi
- `B`: hoạt động với các khoảng trống nhỏ
- `C`: hoạt động một phần, nhầm lẫn hoặc không ổn định đáng kể
- `D`: bị hỏng, không an toàn, hoặc cấu trúc không rõ ràng

## Domain Sản phẩm

| Domain | Điểm | Xác minh | Khả năng đọc của Agent | Độ ổn định Test | Khoảng trống chính | Cập nhật lần cuối |
|--------|-------|-------------|-----------------|---------------|----------|-------------|
| `[domain-a]` | - | - | - | - | - | - |
| `[domain-b]` | - | - | - | - | - | - |
| `[domain-c]` | - | - | - | - | - | - |

## Lớp Kiến trúc

| Lớp | Điểm | Thực thi Ranh giới | Khả năng đọc của Agent | Khoảng trống chính | Cập nhật lần cuối |
|-------|-------|---------------------|-----------------|----------|-------------|
| Types | - | - | - | - | - |
| Services | - | - | - | - | - |
| Runtime | - | - | - | - | - |
| UI | - | - | - | - | - |

## Snapshot Benchmark

| Ngày | Biến thể Harness | Tỷ lệ Hoàn thành | Thử lại | Lỗi trước Review | Ghi chú |
|------|-----------------|----------------|--------|-----------------------|---------|
| YYYY-MM-DD | `[baseline / improved / simplified]` | - | - | - | - |

## Nhật ký Đơn giản hóa

| Ngày | Thành phần Đã xóa | Kết quả | Quyết định |
|------|-------------------|---------|------------|
| YYYY-MM-DD | `[thành phần]` | `[giảm sút / không thay đổi]` | `[khôi phục / giữ đã xóa]` |
