# SOP: Mã hóa Kiến thức Ẩn vào Repo

Sử dụng SOP này khi ngữ cảnh quan trọng vẫn còn trong Google Docs, luồng chat, ticket hoặc trong đầu của mọi người.

## Mục tiêu

Làm cho kiến thức ẩn với agent có thể khám phá được trong codebase để một phiên mới có thể hành động dựa trên nó mà không cần dựa vào hội thoại trước.

## Tín hiệu Kích hoạt

- Agent tiếp tục hỏi cách hệ thống hoạt động.
- Con người nói "chúng tôi đã quyết định điều này trong Slack" hoặc "làm theo những gì X nói tuần trước."
- Các review tham chiếu đến các quy tắc sản phẩm hoặc bảo mật không được viết trong repo.
- Các phiên mới lặp lại công việc khám phá đáng lẽ đã được giải quyết.

## SOP Thực thi

1. Liệt kê các nguồn kiến thức ẩn: tài liệu, chat, quy tắc team mặc nhiên, quyết định bằng miệng.
2. Cho mỗi nguồn, hỏi: đây là kiến trúc, hành vi sản phẩm, chính sách bảo mật, kỳ vọng độ tin cậy, ngữ cảnh kế hoạch hay tài liệu tham khảo?
3. Mã hóa nó vào artifact repo phù hợp:
   - kiến trúc -> `ARCHITECTURE.md`
   - hành vi sản phẩm -> `docs/product-specs/`
   - lý luận thiết kế -> `docs/design-docs/`
   - trạng thái thực thi -> `docs/exec-plans/`
   - tài liệu tham khảo bên ngoài lặp đi lặp lại -> `docs/references/`
   - kỳ vọng chất lượng hoặc độ tin cậy -> `docs/QUALITY_SCORE.md` hoặc `docs/RELIABILITY.md`
4. Thay thế các phát biểu mơ hồ bằng cách diễn đạt hữu ích về mặt vận hành.
5. Xóa hoặc không dùng các bản sao lỗi thời để repo giữ một sự thật có thể khám phá.

## Quy tắc Mã hóa Tốt

- Viết cho khả năng khám phá, không phải cho sự hoàn chỉnh về văn học.
- Ưu tiên các tài liệu ngắn với tên tệp rõ ràng.
- Liên kết các artifact liên quan với nhau.
- Lưu trữ các quy tắc lâu bền, không phải bản ghi cuộc họp.
- Cập nhật repo trong cùng phiên mà quyết định được đưa ra.

## Định nghĩa Hoàn thành

- Một agent mới có thể khám phá quy tắc liên quan mà không cần hỏi con người.
- Cùng một sự thật không bị phân tán qua nhiều tệp mâu thuẫn.
- Artifact mới nằm gần mã hoặc workflow mà nó điều chỉnh.
