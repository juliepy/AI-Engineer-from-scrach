# ARCHITECTURE.md

Ushbu fayl tizimning yuqori darajadagi xaritasidir. U loʻnda boʻlishi va kerak boʻlganda yanada chuqurroq hujjatlarga yoʻnaltirishi kerak.

## Tizim shakli (System Shape)

- Mahsulot: `[mahsulot nomi bilan almashtiring]`
- Asosiy foydalanuvchi jarayoni (workflow): `[asosiy jarayon bilan almashtiring]`
- Runtime muhitlari: `[desktop / web / cli / services / workers]`
- Mahsulotning xatti-harakati uchun yagona haqiqat manbai (Source of truth): `docs/product-specs/`

## Domenlar xaritasi (Domain Map)

| Domen | Maqsad | Asosiy kirish nuqtalari | Tegishli Spec (taʼrif) |
|--------|---------|----------------------|--------------|
| `[domain-a]` | `[u nimaga egalik qiladi]` | `[modullar / marshrutlar / buyruqlar]` | `[spec fayl yoʻli]` |
| `[domain-b]` | `[u nimaga egalik qiladi]` | `[modullar / marshrutlar / buyruqlar]` | `[spec fayl yoʻli]` |

## Qatlamli Model (Layer Model)

Agentlar ixtiyoriy (ad hoc) arxitekturani oʻylab topmasliklari uchun oʻzgarmas (fixed) yoʻnalishli modeldan foydalaning:

`Types -> Config -> Repo -> Service -> Runtime -> UI`

Kesishuvchi (Cross-cutting) masalalar qatlamlararo bevosita ulanmasdan, balki aniq provider yoki adapter chegaralari (boundaries) orqali ulanishi kerak.

## Qatʼiy Bogʻliqlik Qoidalari (Hard Dependency Rules)

- Pastki qatlamlar (lower layers) yuqori qatlamlarga bogʻliq boʻlmasligi shart.
- UI qatlami runtime yoki service interfeyslarini aylanib oʻtmasligi (bypass) kerak.
- Maʼlumotlarga kirish (Data access) doim repozitoriylar yoki shunga ekvivalent adapterlar orqali amalga oshirilishi shart.
- Umumiy utilitalar (shared utilities) doim umumiy (generic) holida qolishi va oʻz ichida domen mantigʻini (domain logic) saqlamasligi shart.
- Yangi bogʻliqliklar (dependencies) mos keluvchi reja yoki dizayn hujjatida (design doc) asoslab berilishi (justified) kerak.

## Kesishuvchi Interfeyslar (Cross-Cutting Interfaces)

| Masala (Concern) | Tasdiqlangan Chegara | Qaydlar (Notes) |
|--------|-------------------|-------|
| Logging va tracing | `[provider / utility yoʻli]` | `[faqatgina structured boʻlsin, ixtiyoriy console ishlatilmasin]` |
| Auth (Avtorizatsiya) | `[provider yoʻli]` | `[token/sessiya qoidalari]` |
| Tashqi APIʼlar | `[client yoki provider yoʻli]` | `[rate limit / retry boʻyicha koʻrsatmalar]` |
| Feature flagʼlar | `[flag chegarasi]` | `[egalik huquqi]` |

## Hozirgi muammoli hududlar (Current Hot Spots)

- `[agentlar uchun xavfsiz oʻzgartirish eng qiyin boʻlgan hudud]`
- `[chegaralari zaif yoki testlari moʻrt boʻlgan hudud]`

## Oʻzgartirishlar uchun tekshiruv (Change Checklist)

Qachonki arxitekturaga tegishli kodga qoʻl ursangiz:

1. Agar domen xaritasi yoki ruxsat etilgan chegaralar (allowed boundaries) oʻzgarsa, ushbu faylni yangilang.
2. Agar ishlash sababi (reasoning) oʻzgarsa, `docs/design-docs/` ichidagi tegishli dizayn hujjatini yangilang.
3. Agar qoidani mexanik ravishda (kod orqali) himoyalash kerak boʻlsa, bajariladigan (executable) tekshiruv (check) qoʻshing yoki yangilang.
