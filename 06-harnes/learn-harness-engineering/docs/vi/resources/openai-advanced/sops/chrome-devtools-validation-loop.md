# SOP: Vòng lặp Xác minh Chrome DevTools

Sử dụng SOP này khi công việc UI phụ thuộc vào tương tác runtime thực tế và screenshot, trạng thái DOM và đầu ra console quan trọng hơn chỉ kiểm tra mã.

## Mục tiêu

Biến xác minh UI thành một vòng lặp tương tác có thể lặp lại mà agent có thể chạy cho đến khi journey sạch sẽ.

## Vòng lặp Cốt lõi

1. Chọn trang mục tiêu hoặc phiên bản ứng dụng.
2. Xóa noise console lỗi thời.
3. Chụp trạng thái TRƯỚC.
4. Kích hoạt đường dẫn UI.
5. Quan sát các sự kiện runtime trong khi tương tác.
6. Chụp trạng thái SAU.
7. Áp dụng sửa chữa và khởi động lại ứng dụng nếu cần.
8. Chạy lại xác minh cho đến khi journey sạch sẽ.

## Đầu vào Bắt buộc

- một lệnh khởi động ổn định
- một UI journey có thể tái tạo
- một cách để snapshot DOM, console hoặc screenshot
- một quy tắc cho những gì được tính là "sạch sẽ"

## SOP Thực thi

1. Viết journey mục tiêu trong kế hoạch active.
2. Định nghĩa thành công theo các thuật ngữ có thể quan sát: văn bản hiện diện, nút được bật, lỗi biến mất, console sạch, yêu cầu thành công.
3. Snapshot trạng thái ban đầu trước khi tương tác.
4. Kích hoạt chính xác một đường dẫn mỗi lần.
5. Ghi lại các sự kiện runtime, thay đổi DOM và đầu ra có thể nhìn thấy.
6. Nếu journey thất bại, hãy sửa lớp chịu trách nhiệm nhỏ nhất và khởi động lại.
7. Chạy lại cùng đường dẫn và so sánh bằng chứng TRƯỚC/SAU.

## Tiêu chí Sạch sẽ

- trạng thái có thể nhìn thấy dự định là hiện diện
- các lỗi không mong đợi vắng mặt
- noise console được hiểu hoặc đã xóa
- chạy lại cùng đường dẫn cho cùng kết quả

## Artifact Repo Cần Cập nhật

- kế hoạch thực thi active
- `docs/RELIABILITY.md` nếu journey trở thành một golden path
- product spec nếu hành vi có thể nhìn thấy thay đổi
