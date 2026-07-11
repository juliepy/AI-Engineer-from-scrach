# OpenAI Ilgʻor SOPʼlari (Advanced SOPs)

Ushbu SOPʼlar (Standart Operatsion Protseduralar) maqoladagi ishlash andozalarini (operating patterns) siz kuzatishingiz yoki moslashtirishingiz mumkin boʻlgan aniq bajarish qoʻllanmalariga (execution playbooks) aylantiradi.

## Kiritilgan SOPʼlar

- [`layered-domain-architecture.md`](./layered-domain-architecture.md): aniq qatlamlar va qatlamlararo kesishuvchi (cross-cutting) chegaralarni belgilash
- [`encode-knowledge-into-repo.md`](./encode-knowledge-into-repo.md): koʻrinmas bilimlarni chat, hujjatlar va xotiradan reponing lokal fayllariga oʻtkazish
- [`observability-feedback-loop.md`](./observability-feedback-loop.md): agentlarga loglar, metrikalar, treyslar va takrorlanuvchi debug siklini (repeatable debug loop) taqdim etish
- [`chrome-devtools-validation-loop.md`](./chrome-devtools-validation-loop.md): UI xatti-harakatlarini toki toza boʻlmaguncha validatsiya qilish uchun brauzer avtomatizatsiyasi va skrinshotlardan (snapshots) foydalanish

## Ulardan Qanday Foydalanish Kerak

1. Joriy muammongizga (bottleneck) mos keladigan SOPʼni tanlang.
2. Yetishmayotgan artefaktlar yoki vositalarni (tooling) oʻrnatish uchun tekshiruv roʻyxatidan (checklist) foydalaning.
3. Hosil boʻlgan qoidalarni oʻzingiz koʻchirib olgan `repo-template/` hujjatlariga kiriting (encode).
4. Qayta-qayta takrorlanadigan tekshiruv (review) izohlarini avtomatlashtirilgan testlar, skriptlar yoki himoya toʻsiqlariga (guardrails) aylantiring.

Bularga koʻr-koʻrona amal qilish shart emas. Ular harnessʼni tushunishni osonlashtirish, qoidalarga majburlay olish (enforceable) va qayta-ishlanuvchan (repeatable) qilishga xizmat qiladi.
