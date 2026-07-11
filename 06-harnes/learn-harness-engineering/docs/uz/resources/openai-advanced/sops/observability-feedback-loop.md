# SOP: Kuzatuvchanlik va Qayta aloqa sikli (Observability Feedback Loop)

Qachonki nosozliklarni izlash (debugging) sekinlashsa, agentlar doimiy ravishda ishni hech qanday dalilsiz (evidence) muvaffaqiyatli yakunlaganini eʼlon qilsa, yoki tizimning ishlashi davomidagi (runtime) xatti-harakatlarni tekshirish shunchaki kodni oʻqishdan koʻra qiyinroq boʻlsa, ushbu SOPʼdan foydalaning.

## Maqsad

Agentga loglar, metrikalar, treyslar va ishga tushirsa boʻladigan ish yuklamalariga (runnable workloads) ega lokal qayta aloqa siklini (local feedback loop) taqdim etish; toki u faqatgina kodga qarab emas, balki real ijro etilishdan (execution) kelib chiqib mulohaza yarata olsin.

## Minimal Stek (Minimum Stack)

- ilova strukturaviy loglarni (structured logs) chiqarishi kerak
- imkon boʻlganda ilova metrikalar (metrics) va treyslarni (traces) chiqarishi kerak
- lokal fan-out (tarqatuvchi) yoki maʼlumot yigʻish (collection) qatlami
- loglar, metrikalar va treyslar uchun soʻrov interfeyslari (query interfaces)
- har bir oʻzgarishdan keyin qayta ishga tushirish mumkin boʻlgan takrorlanuvchi ish yuklamasi (workload) yoki foydalanuvchi jarayoni (user journey)

## Bajarish SOPʼi (Execution SOP)

1. Eng muhim boʻlgan “oltin” runtime jarayonlarni (golden runtime journeys) aniqlab oling.
2. Ishga tushish (startup) va muhim yoʻllarga (critical path) strukturaviy loglar (structured logs) qoʻshing.
3. Kutilish vaqti (latency), muvaffaqiyatsizliklar soni yoki zarur boʻlsa navbat chuqurligi (queue depth) uchun metrikalar qoʻshing.
4. Sekin yoki koʻp bosqichli jarayonlar uchun treyslar yoki vaqt belgilarini (timing markers) qoʻshing.
5. Signallarni lokal dev muhitidan turib soʻrov qilish mumkinligini (queryable) taʼminlang.
6. Agentga qayta ishga tushirishi uchun bitta takrorlanuvchi ish yuklamasi (workload) yoki ssenariy taqdim eting.
7. Ushbu siklni talab qiling: soʻrov (query) -> bogʻlash (correlate) -> xulosa qilish (reason) -> kod yozish (implement) -> qayta ishga tushirish (restart) -> qayta ishga tushirish (rerun) -> tekshirish (verify).

## Debug Sessiyasi Tekshiruvi (Checklist)

- Nima yiqildi (failed)?
- Qaysi signal bu yiqilishni (failure) isbotlaydi?
- Qaysi qatlam ushbu xatolikka ega (owns the failure)?
- Tuzatishdan keyin nima oʻzgardi?
- Ilova toza (cleanly) qayta ishga tushdimi (restart)?
- Qayta ishga tushirilgandan keyin xuddi shu ish yuklamasi tekshiruvdan oʻtdimi (pass)?

## Tugallanganlik Taʼrifi (Definition Of Done)

- Agent xatolik holatini (failure mode) runtime dalillari bilan tushuntirib bera oladi.
- Har bir oʻzgarishdan keyin xuddi shu ish yuklamasini (workload) qayta ishga tushirish mumkin.
- Qayta ishga tushirish (restart) va qayta ishga tushirish (rerun) normal vazifa siklining bir qismiga aylanadi.
- Ishonchlilik signallari (reliability signals) `docs/RELIABILITY.md` da hujjatlashtirilgan.
