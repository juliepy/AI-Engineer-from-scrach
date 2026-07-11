# DESIGN.md

Tệp này là điểm đầu vào thiết kế. Giữ nó ngắn gọn và sử dụng nó để định tuyến vào các tệp chi tiết hơn trong `docs/design-docs/`.

## Mục đích

Ghi lại các quyết định thiết kế sản phẩm và hệ thống lâu bền nên tồn tại vượt ra ngoài một chat, sprint, hoặc bộ nhớ reviewer đơn lẻ.

## Đọc Điều này Khi

- bạn cần triết lý thiết kế hiện tại
- bạn sắp giới thiệu một mẫu mới
- bạn cần biết quyết định thiết kế nào đã được giải quyết so với vẫn đang mở

## Tài liệu Thiết kế Chuẩn

- `docs/design-docs/index.md`: chỉ mục các tài liệu đã được chấp nhận, đề xuất và không dùng nữa
- `docs/design-docs/core-beliefs.md`: niềm tin agent-first toàn dự án

## Quy tắc Thiết kế

- Giữ các tài liệu thiết kế nhỏ và hiện tại.
- Ưu tiên một tài liệu cho mỗi khu vực quyết định.
- Liên kết tài liệu thiết kế từ các kế hoạch và spec khi một thay đổi phụ thuộc vào chúng.
- Nếu một quy tắc thiết kế trở nên quan trọng về mặt vận hành, hãy thúc đẩy nó thành một kiểm tra tự động hoặc cập nhật `ARCHITECTURE.md`.
