# DESIGN.md

Ushbu fayl dizayn uchun kirish nuqtasidir (entrypoint). Uni qisqa saqlang va undan `docs/design-docs/` jildidagi batafsilroq fayllarga yoʻnaltirish (route) uchun foydalaning.

## Maqsad

Bitta suhbatdan (chat), sprintdan yoki tekshiruvchining xotirasidan uzoqroq yashashi kerak boʻlgan doimiy mahsulot (product) va tizim dizayni (system design) qarorlarini yozib boring.

## Buni qachon oʻqish kerak

- joriy dizayn falsafasi (design philosophy) kerak boʻlganda
- yangi andoza (pattern) kiritmoqchi boʻlganingizda
- qaysi dizayn qarorlari qatʼiy qabul qilingan va qaysilari hali ochiqligini bilish uchun

## Asosiy Dizayn Hujjatlari (Canonical Design Docs)

- `docs/design-docs/index.md`: qabul qilingan, taklif qilingan va eskirgan (deprecated) hujjatlar indeksi
- `docs/design-docs/core-beliefs.md`: butun loyihaga taalluqli agent-first (agenti birinchi oʻringa qoʻyadigan) qarashlar

## Dizayn qoidalari

- Dizayn hujjatlarini kichik va eng yangi holatda saqlang.
- Bitta qaror sohasi uchun bitta hujjat boʻlishini afzal koʻring.
- Oʻzgartirish qachonki ularga tayanadigan boʻlsa, reja (plans) va specʼlardan dizayn hujjatlariga havolalar (links) qoʻying.
- Agar dizayn qoidasi operatsion darajada oʻta muhim (operationally critical) boʻlib qolsa, uni avtomatlashtirilgan tekshiruvga (check) aylantiring yoki `ARCHITECTURE.md` ni yangilang.
