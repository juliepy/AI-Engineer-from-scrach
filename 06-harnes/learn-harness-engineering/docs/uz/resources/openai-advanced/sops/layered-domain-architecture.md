# SOP: Qatlamli Domen Arxitekturasi (Layered Domain Architecture)

Qachonki agent doimiy ravishda chegaralarni (boundaries) buzsa, bir xil mantiqni (logic) turli qatlamlarda (layers) takrorlasa yoki bir nechta sessiyadan keyin tekshirish qiyin boʻlib ketadigan kod yozishni boshlasa, ushbu SOPʼdan foydalaning.

## Maqsad

Agentlar strukturani jimgina buzib yubormasdan turib tez ishlay olishi uchun domen chegaralarini (domain boundaries) yetarlicha aniq qilib belgilash.

## Maqsadli Model (Target Model)

Biznes domen (business domain) ichida quyidagi yoʻnalish oqimini afzal koʻring:

`Types -> Config -> Repo -> Service -> Runtime -> UI`

Kesishuvchi (Cross-cutting) masalalar (masalan, auth, telemetry) aniq providerʼlar yoki adapterʼlar orqali ulanishi kerak.
Umumiy (shared) yordamchi funksiyalar (utils) domendan tashqarida qolishi va oʻz ichida domen mantigʻini (domain logic) toʻplamasligi kerak.

## Oʻrnatish Tekshiruvi (Setup Checklist)

- `ARCHITECTURE.md` faylida joriy domenlarni taʼriflang.
- Ruxsat etilgan bogʻliqlik yoʻnalishlarini (allowed dependency directions) `ARCHITECTURE.md` ga yozib qoʻying.
- Auth, telemetry va tashqi APIʼlar kabi qatlamlararo kesishuvchi interfeyslarni (cross-cutting interfaces) yozib qoldiring.
- Hozirgi eng qiyin chegara buzilishi (boundary violation) boʻyicha bitta qisqa eslatma (note) qoʻshing.
- Lint, testlar yoki skriptlar orqali mexanik ravishda nimalar majburiy qilinishi (enforced) kerakligini hal qiling.

## Bajarish SOPʼi (Execution SOP)

1. Kodni qanday uslubda implement qilishga (implementation style) tegishdan oldin kod bazasini (codebase) domenlarga xaritalang (map).
2. Har bir domen uchun ruxsat etilgan qatlamlar ketma-ketligini (allowed layer sequence) aniqlang.
3. Barcha kesishuvchi (cross-cutting) masalalarni toping va ularni providerʼlar yoki adapterʼlar orqali yoʻnaltiring.
4. Tushunarsiz, bir nechta joyda ishlatiladigan mantiqni (shared logic) yo uning egasi boʻlgan domenga yoki haqiqiy umumiy yordamchi funksiyalar (generic utils) safiga koʻchiring.
5. Qoidalarni `ARCHITECTURE.md` da hujjatlashtiring.
6. Eng koʻp xarajat (cost) talab qiladigan qoidabuzilish (violation) uchun bitta bajariladigan (executable) himoya (guardrail) qoʻshing.
7. Oʻzgarishlardan soʻng sifat bahosini (quality scoring) yangilang.

## Tugallanganlik Taʼrifi (Definition Of Done)

- Yangi qoʻshilgan agent maʼlum bir oʻzgarish (change) qaysi qatlamga tegishliligini ayta oladi.
- UI kodi endi repo yoki tashqi tizimlarga bevosita taʼsir (external side effects) qilmaydi.
- Kesishuvchi masalalarning maxsus kirish nuqtalari (named entry points) bor.
- Kamida bitta muhim chegara (boundary) mexanik ravishda (kod orqali) himoyalangan.

## Yangilanishi Kerak Boʻlgan Repo Artefaktlari

- `ARCHITECTURE.md`
- `docs/QUALITY_SCORE.md`
- Qachonki asosiy sabablar (rationale) oʻzgarsa `docs/design-docs/`
- `docs/PLANS.md` yoki faol ishlash rejasi (active execution plan)
