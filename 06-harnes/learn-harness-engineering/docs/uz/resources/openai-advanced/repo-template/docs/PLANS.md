# PLANS.md

Bu fayl ijro rejalari (execution plans) qanday yaratilishi, yangilanishi, yakunlanishi va arxivlanishini belgilaydi.

## Qachon reja tuzish majburiydir (When A Plan Is Required)

Agar ish quyidagi shartlarga tushsa ijro rejasini tuzing:

- bir nechta sessiyani qamrab olsa
- bittadan ortiq tizim boʻlagini (subsystem) oʻzgartirsa
- tekshiruv yoki tarqatish xavfi (rollout risk) yuqori boʻlsa
- qayd etilishi kerak boʻlgan ochiq qarorlarga bogʻliq boʻlsa

## Reja manzillari (Plan Locations)

- `docs/exec-plans/active/`: ayni vaqtda boshqarilayotgan (driving) rejalar
- `docs/exec-plans/completed/`: kelajakdagi agent konteksti uchun saqlab qoʻyilgan yakunlangan rejalar
- `docs/exec-plans/tech-debt-tracker.md`: keyinga qoldirilgan ishlar va qoʻshimchalar (follow-ups)

## Minimal reja boʻlimlari

- maqsad (objective)
- qamrov (scope) va qamrovdan tashqari qismlar (out-of-scope)
- tekshirish yoʻli (verification path)
- xavflar va toʻsqinliklar (risks and blockers)
- jarayon jurnali (progress log)
- ochiq qarorlar (open decisions)

## Ishlash Qoidalari (Operating Rules)

- Bitta faol rejada bitta aniq egalik qilinuvchi joriy qadam (owned current step) boʻlishi kerak.
- Ish davom etgani sari rejani yangilab boring; unga oddiy oʻzgarmas matn (static prose) sifatida qaramang.
- Agar qaror implementatsiya (kod yozish) yoʻnalishini oʻzgartirsa, uni rejaga yozib qoʻying.
- Agentlar oldingi kontekstni osongina topishi uchun yakunlangan rejalarni `completed/` jildiga koʻchiring.
