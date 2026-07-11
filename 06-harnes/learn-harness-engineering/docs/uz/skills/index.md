# Koʻnikmalar (Skills)

Ushbu katalog kurs bilan birga taqdim etiladigan AI agent koʻnikmalarini (skills) oʻz ichiga oladi. Koʻnikmalar (Skills) — maxsus vazifalarni bajarish uchun AI kod yozuvchi agentlari (Claude Code, Codex, Cursor, Windsurf va boshqalar) tomonidan yuklanishi mumkin boʻlgan mustaqil (self-contained) prompt andozalaridir.

## harness-creator

AI kod yozuvchi agentlari uchun ishlab chiqarish darajasidagi (production-grade) harness muhandisligi koʻnikmasi (skill). U sizga beshta asosiy harness quyi tizimini (subsystems): yoʻriqnomalar (instructions), holat (state), tekshiruv (verification), skoup (scope) va sessiya yashash siklini (session lifecycle) yaratish, baholash (assess) va yaxshilashda yordam beradi.

### U nima qiladi (What It Does)

- **Harnessʼlarni noldan yaratish** — AGENTS.md, funksiyalar roʻyxati (feature lists), tekshiruv jarayonlari (verification workflows)
- **Mavjud harnessʼlarni yaxshilash** — Eng muhim oʻzgarishlarni belgilagan holda besh quyi tizim boʻyicha baholash
- **Sessiya uzluksizligini (Session continuity) loyihalash** — Xotirani saqlab qolish (Memory persistence), jarayonni kuzatish (progress tracking), topshirish jarayonlari (handoff procedures)
- **Ishlab chiqarish andozalarini qoʻllash** — Xotira, kontekst muhandisligi, vositalar xavfsizligi, koʻp agentli muvofiqlashtirish

### Tez boshlash (Quick Start)

Koʻnikma fayllari repozitoriyning [`skills/harness-creator/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/skills/harness-creator) qismida joylashgan.

```bash
npx skills add walkinglabs/learn-harness-engineering --skill harness-creator
```

Undan Claude Code bilan foydalanish uchun, `harness-creator/` jildini loyihangizning koʻnikmalar (skills) yoʻliga koʻchiring yoki agentingizni SKILL.md fayliga yoʻnaltiring.

### Maʼlumotnoma andozalari (Reference Patterns)

Ushbu koʻnikma oʻz ichiga 7 ta yoʻnaltirilgan maʼlumotnoma hujjatini (reference documents) oladi:

| Andoza (Pattern) | Qachon foydalanish kerak |
|---------|-------------|
| Xotirani saqlab qolish (Memory Persistence) | Agent sessiyalar oʻrtasida unutib qoʻysa |
| Skill Runtime | Qayta ishlatiladigan workflowʼlarni skill sifatida paketlash |
| Kontekst muhandisligi (Context Engineering) | Kontekst byudjetini boshqarish, kerak vaqtda (JIT) yuklash |
| Vositalar reyestri (Tool Registry) | Vositalar xavfsizligi, parallellik nazorati (concurrency control) |
| Koʻp agentli muvofiqlashtirish (Multi-Agent Coordination) | Parallellik, ixtisoslashish (specialization) jarayonlari |
| Yashash sikli va Bootstrap (Lifecycle & Bootstrap) | Hookʼlar, fon vazifalari (background tasks), inisializatsiya |
| Tuzoqlar (Gotchas) | 15 ta koʻzga tashlanmaydigan xato turlari va ularning yechimlari |

### Andozalar (Templates)

Koʻnikma oʻz ichiga foydalanishga tayyor andozalarni oladi:

- `agents.md` — Ishlash qoidalari kiritilgan AGENTS.md qolipi (scaffold)
- `feature-list.json` — JSON Schema + namunaviy funksiyalar roʻyxati (example feature list)
- `init.sh` — Standart inisializatsiya skripti
- `progress.md` — Sessiya jarayoni jurnali (progress log) andozasi
- `session-handoff.md` — Sessiyani topshirish andozasi

### Skriptlar

Koʻnikma scaffold, tekshirish, HTML baholash hisoboti va strukturaviy benchmark hisoboti uchun sof Node.js skriptlarini ham oʻz ichiga oladi.

### Ushbu koʻnikma qanday yaratilgan (How This Skill Was Built)

`harness-creator`, agent koʻnikmalarini (skills) yaratish, test qilish va iteratsiya qilish uchun Anthropicʼning rasmiy meta-koʻnikmasi boʻlgan **skill-creator** metodologiyasidan foydalanib ishlab chiqilgan. skill-creator oʻzida oʻrnatilgan eval ishga tushiruvchilar (eval runners), baholovchilar (graders) va benchmark koʻruvchisi (benchmark viewer) bilan tuzilmali jarayonni (qoralama → test → baholash → iteratsiya) taqdim etadi.

- **skill-creator manbasi**: [anthropics/skills — skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator)
- **Claude Code skills hujjatlari**: [anthropics/claude-code — plugin-dev/skills](https://github.com/anthropics/claude-code/tree/main/plugins/plugin-dev/skills)
