# Inisializatsiya agenti boʻyicha qoʻllanma (Initializer Agent Playbook)

Ushbu qoʻllanmadan repozitoriydagi birinchi jiddiy sessiya uchun, qismlarga boʻlingan funksiya (incremental feature) ishlari boshlanishidan avval foydalaning.

## Maqsad

Keyingi sessiyalar ishga tushirish buyruqlarini (startup commands), joriy holatni (current status) yoki vazifa chegaralarini (task boundaries) boshqatdan izlab oʻtirmasdan toʻgʻridan-toʻgʻri ishlashga oʻta olishi uchun barqaror operatsion sirt (stable operating surface) yarating.

## Talab qilinadigan Natijalar

Inisializatsiya agenti (initializer) oʻzidan keyin kamida quyidagi artefaktlarni qoldirishi kerak:

- `AGENTS.md` yoki `CLAUDE.md` kabi asosiy yoʻriqnoma fayli (root instruction file)
- `feature_list.json` kabi mashina oʻqiy oladigan funksiyalar roʻyxati yuzasi
- `claude-progress.md` kabi doimiy saqlanadigan jarayon (progress) artefakti
- `init.sh` kabi standart ishga tushirish yordamchisi
- bazaviy kod skeletini oʻz ichiga olgan dastlabki xavfsiz commit

## Tekshiruv roʻyxati (Checklist)

1. Standart ishga tushirish yoʻlini belgilang.
2. Standart tekshiruv yoʻlini (verification path) belgilang.
3. Jarayon jurnalini (progress log) yarating va boshlangʻich holatni yozib qoldiring.
4. Ishni oʻz holatlariga ega boʻlgan aniq funksiyalarga ajrating.
5. Birinchi toza bazaviy commitʼni (clean baseline commit) yarating.

## Muvaffaqiyat testi (Success Test)

Hech qanday avvalgi chat kontekstiga ega boʻlmagan butunlay yangi sessiya quyidagilarga javob bera olishi kerak:

- bu repozitoriy nima ish qiladi
- uni qanday ishga tushirish kerak
- uni qanday tekshirish (verify) kerak
- nimalar tugallanmagan
- keyingi eng yaxshi qadam nima boʻlishi kerak
