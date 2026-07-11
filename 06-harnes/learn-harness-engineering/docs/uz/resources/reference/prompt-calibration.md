# Promptni sozlash (Prompt Calibration)

Asosiy (root) yoʻriqnomalar har bir mumkin boʻlgan harakatni emas, balki ishlash tizimini (operating frame) belgilashi kerak.

## Asosiy (Root) faylda qoldiring

- repozitoriy maqsadi va skoupi (scope)
- ishga tushirish (startup) yoʻli
- tekshirish (verification) yoʻli
- muhokama qilinmaydigan qatʼiy cheklovlar
- talab qilinadigan holat artefaktlari (state artifacts)
- sessiya yakuni qoidalari

## Asosiy fayldan olib tashlang

- juda uzun tarixiy chetki holatlar (edge cases)
- maʼlum bir mavzuga xos implementatsiya detallari
- bevosita kodning yonida turishi kerak boʻlgan lokal arxitektura eslatmalari
- faqatgina bitta kichik tizim (subsystem) ga taalluqli boʻlgan misollar

## Ish qoidasi

Asosiy fayl (root file) mutlaqo yangi sessiyaning tezda oʻziga kelib olishiga yordam berishi kerak. Agar fayl oʻtmishdagi barcha xatoliklarni tashlaydigan axlatxonaga aylanib borayotgan boʻlsa, maʼlumotlarni kichikroq hujjatlarga boʻling va ular oʻrniga oʻsha hujjatlarga havolalar qoldiring (link to them).
