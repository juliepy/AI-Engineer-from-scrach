# AGENTS.md

Kho lưu trữ này được tối ưu hóa cho công việc coding-agent chạy lâu. Giữ tệp này ngắn. Sử dụng nó như lớp định tuyến vào các tài liệu hệ thống ghi chép, không phải như một đống hướng dẫn khổng lồ.

## Quy trình Khởi động

Trước khi thay đổi mã:

1. Xác nhận thư mục gốc repo bằng `pwd`.
2. Đọc `ARCHITECTURE.md` để biết bản đồ hệ thống hiện tại và các quy tắc phụ thuộc cứng.
3. Đọc `docs/QUALITY_SCORE.md` để xem domain hoặc lớp nào yếu nhất.
4. Đọc `docs/PLANS.md`, sau đó mở kế hoạch active bạn đang làm việc từ đó.
5. Đọc spec sản phẩm liên quan trong `docs/product-specs/`.
6. Chạy đường dẫn bootstrap và xác minh chuẩn cho repo này.
7. Nếu xác minh baseline đang thất bại, hãy sửa baseline trước khi thêm phạm vi.

## Bản đồ Định tuyến

- `ARCHITECTURE.md`: bản đồ domain, mô hình lớp, quy tắc phụ thuộc
- `docs/design-docs/index.md`: các quyết định thiết kế và niềm tin cốt lõi
- `docs/product-specs/index.md`: các hành vi sản phẩm hiện tại và mục tiêu chấp nhận
- `docs/PLANS.md`: vòng đời kế hoạch và chính sách kế hoạch thực thi
- `docs/QUALITY_SCORE.md`: sức khỏe domain sản phẩm và lớp
- `docs/RELIABILITY.md`: tín hiệu runtime, benchmark và kỳ vọng khởi động lại
- `docs/SECURITY.md`: bí mật, sandbox, dữ liệu và quy tắc hành động bên ngoài
- `docs/FRONTEND.md`: ràng buộc UI, quy tắc design system, kiểm tra accessibility

## Hợp đồng Làm việc

- Làm việc từ một kế hoạch có ranh giới hoặc slice tính năng tại một thời điểm.
- Không đánh dấu công việc xong chỉ từ kiểm tra mã; cần bằng chứng có thể chạy được.
- Nếu bạn thay đổi hành vi, hãy cập nhật tài liệu sản phẩm, kế hoạch hoặc độ tin cậy phù hợp trong cùng phiên.
- Nếu bạn thấy phản hồi review lặp đi lặp lại, hãy thúc đẩy nó thành quy tắc cơ học, kiểm tra hoặc linter thay vì giải thích lại trong chat.
- Giữ tài liệu được tạo ra trong `docs/generated/` và tài liệu tham khảo nguồn trong `docs/references/`.
- Ưu tiên thêm tài liệu nhỏ, hiện tại hơn là phát triển tệp này.

## Định nghĩa Hoàn thành

Một thay đổi chỉ xong khi tất cả những điều sau đây là đúng:

- hành vi mục tiêu đã được triển khai
- xác minh cần thiết đã thực sự chạy
- bằng chứng được liên kết từ kế hoạch hoặc tài liệu chất lượng liên quan
- các tài liệu bị ảnh hưởng vẫn là hiện tại
- kho lưu trữ có thể khởi động lại sạch sẽ từ đường dẫn khởi động chuẩn

## Cuối Phiên

Trước khi kết thúc phiên:

1. Cập nhật kế hoạch thực thi active.
2. Cập nhật `docs/QUALITY_SCORE.md` nếu bất kỳ domain hoặc lớp nào thay đổi có ý nghĩa.
3. Ghi lại nợ mới trong `docs/exec-plans/tech-debt-tracker.md` nếu bạn đã hoãn nó.
4. Di chuyển các kế hoạch đã hoàn thành sang `docs/exec-plans/completed/` khi phù hợp.
5. Để repo ở trạng thái có thể khởi động lại với hành động tiếp theo rõ ràng.
