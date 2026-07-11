# SOP: Koʻrinmas Bilimlarni Repo Ichiga Kodlashtirish (Encode Unseen Knowledge Into The Repo)

Qachonki muhim kontekst haligacha Google Docs hujjatlarida, chat yozishmalarida, chiptalarda (tickets) yoki odamlarning kallasida saqlanayotgan boʻlsa, ushbu SOPʼdan foydalaning.

## Maqsad

Agent koʻra olmaydigan bilimlarni kod bazasida (codebase) topish mumkin boʻladigan holatga keltirish, toki yangi boshlangan sessiya (fresh session) oldingi suhbatlarga tayangan holda ish yuritishga majbur boʻlmasin.

## Trigger Signallari

- Agent tizim qanday ishlashi haqida qayta-qayta soʻrayversa.
- Odamlar “biz buni Slackʼda hal qilgandik” yoki “oʻtgan hafta X nima degan boʻlsa, shuni qiling” deyishsa.
- Tekshiruvlar (reviews) davomida repoda yozilmagan mahsulot (product) yoki xavfsizlik (security) qoidalari aytib oʻtilsa.
- Yangi sessiyalar aslida hal qilinib boʻlingan masalalarni qaytadan “kashf qilishga” vaqt sarflayotsa.

## Bajarish SOPʼi (Execution SOP)

1. Koʻrinmas bilimlar manbalarini (invisible knowledge sources) roʻyxat qilib yozing: docs (hujjatlar), chatlar, yozilmagan jamoa qoidalari (tacit team rules), ogʻzaki qarorlar.
2. Har bir manba uchun soʻrang: bu arxitekturami, mahsulotning ishlashi (product behavior), xavfsizlik siyosati, ishonchlilik kutilmasimi (reliability expectation), reja kontekstimi yoki biror maʼlumotnomami (reference material)?
3. Uni mos keluvchi repo artefaktiga joylashtiring (encode):
   - arxitektura -> `ARCHITECTURE.md`
   - mahsulotning ishlashi -> `docs/product-specs/`
   - dizayn sabablari (design rationale) -> `docs/design-docs/`
   - ish holatlari (execution state) -> `docs/exec-plans/`
   - takrorlanuvchi tashqi maʼlumotlar -> `docs/references/`
   - sifat yoki ishonchlilik kutilmalari -> `docs/QUALITY_SCORE.md` yoki `docs/RELIABILITY.md`
4. Noaniq va umumiy gaplarni (vague statements) amaliyotda ishlatish mumkin boʻlgan aniq jumlalarga aylantiring.
5. Repo yagona izlab topish mumkin boʻlgan haqiqat manbai (discoverable truth) boʻlib qolishi uchun, eskirgan nusxalarni (stale copies) oʻchiring yoki bekor qiling (deprecate).

## Yaxshi Kodlashtirish (Encoding) Qoidalari

- Badiiy mukammallik (literary completeness) uchun emas, topish oson boʻlishi uchun (discoverability) yozing.
- Fayl nomlari aniq va tushunarli boʻlgan qisqa hujjatlarni afzal koʻring.
- Bir-biriga aloqador artefaktlarni oʻzaro bogʻlang (link).
- Uchrashuv transkriptlarini emas, balki doimiy ishlaydigan qoidalarni saqlang.
- Biror qaror qabul qilingan oʻsha sessiyaning oʻzidayoq reponi yangilang.

## Tugallanganlik Taʼrifi (Definition Of Done)

- Yangi agent muhim qoidani inson aralashuvisiz topa olishi kerak.
- Ayni bitta fakt (qoida) bir nechta bir-biriga zid boʻlgan (contradictory) fayllarda tarqalib ketmasligi kerak.
- Yangi artefakt u boshqaradigan (governs) kod yoki ish oqimi (workflow) ning bevosita yonida joylashgan boʻlishi kerak.
