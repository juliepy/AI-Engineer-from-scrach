# PRODUCT_SENSE.md

Bu fayl agentlar faqat kodga qarab ishonchli xulosa chiqara olmaydigan uzoq muddatli mahsulot yondashuvini (durable product judgment) oʻzida saqlaydi.

## Mahsulot Asosi (Product Core)

- Asosiy foydalanuvchi: `[almashtiring]`
- Bajarilishi kerak boʻlgan ish (Job to be done): `[almashtiring]`
- Bartaraf etilishi kerak boʻlgan asosiy toʻsiq (frustration): `[almashtiring]`
- Qabul qilish uchun sifat darajasi (Quality bar for acceptance): `[almashtiring]`

## Mahsulot Qoidalari (Product Rules)

- Funksiyalar sonidan koʻra, foydalanuvchiga koʻrinadigan ishonchlilikni (user-visible reliability) ustun qoʻying.
- Noaniq xatti-harakatlarni taxmin qilishga (guess) ruxsat deb emas, balki spec (spetsifikatsiya) dagi boʻshliq sifatida qabul qiling.
- Agar kod yozish foydalanuvchi koʻradigan yoki ishonadigan narsani oʻzgartirsa, tegishli specni (matching spec) yangilang.
- Aniq jarayonlar (concrete flows) uchun mahsulot speclaridan, va mahsulotdagi kesishuvchi ustuvorliklar (cross-cutting priorities) uchun ushbu fayldan foydalaning.

## Qatʼiyan Taqiqlangan Andozalar (No-Go Patterns)

- Yashirin buzgʻunchi operatsiyalar (destructive actions)
- Foydalanuvchiga hech qanday bildirishnomasiz jimgina xatolik yuz berishi (Silent failure)
- Koʻrinadigan holat (visible state) uchun aniq yagona haqiqat manbai (source of truth) yoʻqligi
- Bir jumlada tushuntirib boʻlmaydigan funksiyalar (features)
