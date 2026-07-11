[English Version →](../../../en/resources/openai-advanced/) | [中文版本 →](../../../zh/resources/openai-advanced/)

# Gói Harness Nâng cao OpenAI

Gói này tập hợp thiết kế harness được mô tả trong bài viết "Harness Engineering" của OpenAI thành một bộ tệp bắt đầu có thể áp dụng và cấu trúc SOP đi kèm.

## Tại sao Nó Tồn tại

Bài viết harness engineering mô tả các nguyên tắc cấp cao: kho lưu trữ là hệ thống ghi chép, bộ nhớ ngoại hóa, kiểm tra cơ học thay vì ký ức, và các vòng phản hồi phục hồi. Gói này biến các nguyên tắc đó thành:

- bộ tài liệu cấu trúc rõ ràng cho một repo thực tế
- tính điểm chất lượng theo domain sản phẩm và lớp kiến trúc
- thư mục tài liệu tham khảo thân thiện với model
- các quy trình vận hành chuẩn cho kiến trúc, thu thập kiến thức, và xác minh runtime

## Bố cục Bắt đầu Có sẵn

Gói bắt đầu trong [`repo-template/`](./repo-template/index.md) phản ánh cấu trúc dưới đây:

```text
AGENTS.md
ARCHITECTURE.md
docs/
├── design-docs/
│   ├── index.md
│   └── core-beliefs.md
├── exec-plans/
│   ├── active/
│   ├── completed/
│   └── tech-debt-tracker.md
├── generated/
│   └── db-schema.md
├── product-specs/
│   ├── index.md
│   └── new-user-onboarding.md
├── references/
│   ├── design-system-reference-llms.txt
│   ├── nixpacks-llms.txt
│   └── uv-llms.txt
├── DESIGN.md
├── FRONTEND.md
├── PLANS.md
├── PRODUCT_SENSE.md
├── QUALITY_SCORE.md
├── RELIABILITY.md
└── SECURITY.md
```

## Cách Áp dụng Nó

1. Bắt đầu từ gói tối giản nếu repo của bạn vẫn còn nhỏ.
2. Sao chép các tệp trong [`repo-template/`](./repo-template/index.md) vào kho lưu trữ của bạn khi bạn cần cấu trúc mạnh hơn.
3. Giữ `AGENTS.md` ngắn. Coi nó như bộ định tuyến vào các tài liệu sâu hơn, không phải như bách khoa toàn thư.
4. Cập nhật các tài liệu chất lượng, độ tin cậy và kế hoạch như một phần của công việc thông thường, không phải như một ngày dọn dẹp riêng biệt.
5. Giữ các artifact được tạo ra và tài liệu tham khảo bên ngoài rõ ràng để agent có thể tìm thấy chúng mà không cần dựa vào lịch sử chat.

## Thư viện SOP

Thư mục [`sops/`](./sops/index.md) biến các sơ đồ của bài viết thành các quy trình vận hành từng bước:

- thiết lập kiến trúc domain phân lớp
- mã hóa kiến thức ẩn vào kho lưu trữ
- stack observability cục bộ và workflow vòng phản hồi
- vòng lặp xác minh Chrome DevTools cho công việc UI

## Nguyên tắc Thiết kế

- Điểm đầu vào ngắn, tài liệu liên kết sâu hơn
- Kho lưu trữ là hệ thống ghi chép
- Kiểm tra cơ học tốt hơn các quy tắc được nhớ
- Kế hoạch và lịch sử chất lượng nằm bên cạnh mã
- Dọn dẹp và đơn giản hóa là trách nhiệm hạng nhất

Gói này có chủ ý theo quan điểm, nhưng nó vẫn nên được điều chỉnh cho dự án của bạn thay vì sao chép mù quáng.
