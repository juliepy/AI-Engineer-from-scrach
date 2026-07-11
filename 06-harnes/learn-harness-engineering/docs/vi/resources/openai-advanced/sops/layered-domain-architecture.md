# SOP: Kiến trúc Domain Phân lớp

Sử dụng SOP này khi agent tiếp tục vi phạm ranh giới, sao chép logic qua các lớp, hoặc tạo ra mã khó review sau một vài phiên.

## Mục tiêu

Làm cho ranh giới domain đủ rõ ràng để agent có thể di chuyển nhanh mà không âm thầm làm xuống cấp cấu trúc.

## Mô hình Mục tiêu

Trong một domain kinh doanh, ưu tiên luồng định hướng này:

`Types -> Config -> Repo -> Service -> Runtime -> UI`

Các mối quan tâm xuyên suốt nên đi vào qua các provider hoặc adapter rõ ràng. Các utils dùng chung nằm bên ngoài domain và không nên tích lũy logic domain.

## Danh sách Kiểm tra Thiết lập

- Định nghĩa các domain hiện tại trong `ARCHITECTURE.md`.
- Viết các hướng phụ thuộc được phép trong `ARCHITECTURE.md`.
- Ghi lại các giao diện xuyên suốt như auth, telemetry và external API.
- Thêm một ghi chú ngắn cho vi phạm ranh giới khó nhất hiện tại.
- Quyết định những gì nên được thực thi cơ học bởi lint, test hoặc script.

## SOP Thực thi

1. Ánh xạ codebase thành các domain trước khi chạm vào phong cách triển khai.
2. Cho mỗi domain, xác định chuỗi lớp được phép.
3. Xác định tất cả các mối quan tâm xuyên suốt và định tuyến chúng qua các provider hoặc adapter.
4. Di chuyển logic dùng chung mơ hồ sang domain sở hữu hoặc sang utils thực sự chung chung.
5. Ghi lại các quy tắc trong `ARCHITECTURE.md`.
6. Thêm một guardrail có thể thực thi cho vi phạm có chi phí cao nhất.
7. Cập nhật điểm chất lượng sau khi thay đổi.

## Định nghĩa Hoàn thành

- Một agent mới có thể biết lớp nào sở hữu một thay đổi.
- Mã UI không còn tiếp cận vào repo hoặc side effect bên ngoài trực tiếp.
- Các mối quan tâm xuyên suốt có các điểm đầu vào được đặt tên.
- Ít nhất một ranh giới quan trọng được thực thi cơ học.

## Artifact Repo Cần Cập nhật

- `ARCHITECTURE.md`
- `docs/QUALITY_SCORE.md`
- `docs/design-docs/` khi lý luận thay đổi
- `docs/PLANS.md` hoặc kế hoạch thực thi active
