# AGENTS.md

Ushbu repozitoriy kod yozuvchi agentlarning uzoq davom etadigan (long-running) ishlari uchun optimallashtirilgan. Ushbu faylni qisqa saqlang. Uni barcha yoʻriqnomalar toʻkib tashlangan ulkan axlatxona sifatida emas, balki yagona haqiqat manbai (system-of-record) hujjatlariga yoʻnaltiruvchi marshrutizatsiya (routing) qatlami sifatida ishlating.

## Ishga tushirish oqimi (Startup Workflow)

Kodni oʻzgartirishdan oldin:

1. `pwd` yordamida repo root jildini tasdiqlang.
2. Joriy tizim xaritasi (system map) va qatʼiy bogʻliqlik (hard dependency) qoidalari bilan tanishish uchun `ARCHITECTURE.md` ni oʻqing.
3. Qaysi domenlar yoki qatlamlar eng zaif ekanligini koʻrish uchun `docs/QUALITY_SCORE.md` ni oʻqing.
4. `docs/PLANS.md` ni oʻqing, soʻngra hozir qaysi biri ustida ishlayotgan boʻlsangiz, oʻsha faol rejani (active plan) oching.
5. `docs/product-specs/` dan tegishli mahsulot taʼrifini (product spec) oʻqing.
6. Ushbu repo uchun standart ishga tushirish (bootstrap) va tekshirish (verification) yoʻlini ishga tushiring.
7. Agar bazaviy tekshiruv (baseline verification) yiqilayotgan boʻlsa, skoupni (scope) kengaytirishdan avval bazaviy holatni (baseline) toʻgʻrilang.

## Marshrutizatsiya Xaritasi (Routing Map)

- `ARCHITECTURE.md`: domen xaritasi, qatlamlar modeli, bogʻliqlik qoidalari
- `docs/design-docs/index.md`: dizayn qarorlari va asosiy qarashlar (core beliefs)
- `docs/product-specs/index.md`: joriy mahsulot xatti-harakatlari va qabul qilish (acceptance) maqsadlari
- `docs/PLANS.md`: reja yashash sikli (lifecycle) va ijro etish rejalari siyosati (execution-plan policy)
- `docs/QUALITY_SCORE.md`: mahsulot-domeni (product-domain) va qatlamlar salomatligi
- `docs/RELIABILITY.md`: runtime signallar, benchmarklar va qayta ishga tushish (restart) kutilmalari
- `docs/SECURITY.md`: maxfiy kalitlar (secrets), izolyatsiya (sandbox), maʼlumotlar (data) va tashqi operatsiyalar qoidalari
- `docs/FRONTEND.md`: UI cheklovlari, dizayn tizimi qoidalari, foydalanish imkoniyatlari (accessibility) tekshiruvlari

## Ishlash shartnomasi (Working Contract)

- Bir vaqtning oʻzida faqat bitta belgilangan reja yoki funksiya boʻlagi (feature slice) ustida ishlang.
- Faqatgina kodga qarab tahlil qilish bilangina ishni tugallandi deb hisoblamang; ishga tushirib koʻrish (runnable) orqali olingan dalil (evidence) talab qilinadi.
- Agar xatti-harakatni (behavior) oʻzgartirsangiz, oʻsha sessiyaning oʻzidayoq tegishli mahsulot (product), reja yoki ishonchlilik (reliability) hujjatlarini ham yangilang.
- Agar tekshiruvda (review) qayta-qayta bir xil izohni (feedback) koʻrsangiz, uni chatda tushuntirib oʻtirishning oʻrniga mexanik qoidaga, skript tekshiruviga (check) yoki linterʼga aylantiring (promote).
- Avtomat yaratilgan (generated) materiallarni `docs/generated/` jildida va manba maʼlumotlarini (source references) `docs/references/` jildida saqlang.
- Ushbu faylni shishirib yuborishdan koʻra, kichikroq va yangi hujjatlar qoʻshishni afzal koʻring.

## Tugallanganlik Taʼrifi (Definition Of Done)

Oʻzgartirish quyidagilarning barchasi toʻgʻri boʻlgandagina tugatilgan deb hisoblanadi:

- maqsad qilingan xatti-harakat (target behavior) toʻliq amalga oshirilgan
- talab qilingan tekshiruv (verification) haqiqatda bajarilgan
- dalillar (evidence) tegishli reja yoki sifat (quality) hujjatiga bogʻlangan (linked)
- taʼsir qilgan hujjatlar (affected docs) eng yangi holatda yangilangan boʻlsa
- repozitoriy standart ishga tushirish (startup) yoʻli orqali xatosiz (cleanly) qayta ishga tusha olsa

## Sessiya Yakuni (End Of Session)

Sessiyani yakunlashdan oldin:

1. Faol ishlash rejasini (active execution plan) yangilang.
2. Agar biron domen yoki qatlam mazmunan oʻzgargan boʻlsa `docs/QUALITY_SCORE.md` ni yangilang.
3. Agar yangi texnik qarz (technical debt) ni keyinga qoldirsangiz, uni `docs/exec-plans/tech-debt-tracker.md` da yozib qoʻying.
4. Tugallangan rejalarni oʻz vaqtida `docs/exec-plans/completed/` papkasiga koʻchiring.
5. Reponi qayta ishga tushib keta oladigan holatda (restartable state) hamda keyingi amal aniq koʻrsatilgan qilib qoldiring.
