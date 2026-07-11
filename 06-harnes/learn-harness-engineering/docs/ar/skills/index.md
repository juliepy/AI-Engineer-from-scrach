# المهارات

يحتوي هذا المجلد على مهارات وكلاء الذكاء الاصطناعي المرفقة مع هذا المساق. المهارات هي قوالب prompt مستقلة يمكن لوكلاء البرمجة مثل Claude Code و Codex و Cursor و Windsurf تحميلها لتنفيذ مهام متخصصة.

## harness-creator

مهارة harness engineering بمستوى إنتاجي لوكلاء البرمجة بالذكاء الاصطناعي. تساعدك على إنشاء وتقييم وتحسين الأنظمة الفرعية الخمسة الأساسية لأي harness: التعليمات، الحالة، التحقق، النطاق، ودورة حياة الجلسة.

### ماذا تفعل

- **إنشاء harnesses من الصفر** — AGENTS.md، قوائم ميزات، workflows للتحقق
- **تحسين harnesses موجودة** — تقييم للأنظمة الفرعية الخمسة مع تحسينات ذات أولوية
- **تصميم استمرارية الجلسات** — ذاكرة دائمة، تتبع التقدم، وإجراءات handoff
- **تطبيق أنماط إنتاجية** — الذاكرة، context engineering، أمان الأدوات، والتنسيق متعدد الوكلاء

### بداية سريعة

توجد ملفات المهارة في المستودع ضمن [`skills/harness-creator/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/skills/harness-creator).

```bash
npx skills add walkinglabs/learn-harness-engineering --skill harness-creator
```

لاستخدامها مع Claude Code، انسخ مجلد `harness-creator/` إلى مسار المهارات في مشروعك، أو وجه الوكيل إلى ملف SKILL.md.

### أنماط مرجعية

تتضمن المهارة 7 وثائق مرجعية مركزة:

| النمط | متى تستخدمه |
|---------|-------------|
| Memory Persistence | عندما ينسى الوكيل بين الجلسات |
| Skill Runtime | تغليف workflows قابلة لإعادة الاستخدام كمهارات |
| Context Engineering | إدارة ميزانية السياق والتحميل عند الحاجة |
| Tool Registry | أمان الأدوات والتحكم في التوازي |
| Multi-Agent Coordination | التوازي و workflows التخصص |
| Lifecycle & Bootstrap | hooks، مهام الخلفية، والتهيئة |
| Gotchas | 15 نمط فشل غير بديهي مع حلول |

### القوالب

تضم المهارة قوالب جاهزة للاستخدام:

- `agents.md` — هيكل AGENTS.md مع قواعد عمل
- `feature-list.json` — JSON Schema ومثال قائمة ميزات
- `init.sh` — سكربت تهيئة قياسي
- `progress.md` — قالب سجل تقدم الجلسة
- `session-handoff.md` — قالب تسليم الجلسة

### Scripts

تتضمن المهارة أيضا scripts نقية بـ Node.js لإنشاء scaffold والتحقق وتقارير HTML و benchmark بنيوي.

### كيف بُنيت هذه المهارة

طُورت `harness-creator` باستخدام منهجية **skill-creator**، وهي meta-skill الرسمية من Anthropic لإنشاء مهارات الوكلاء واختبارها وتحسينها تكراريًا. توفر skill-creator workflow منظمًا: مسودة → اختبار → تقييم → تكرار، مع مشغلات eval ومصححات وواجهة benchmark.

- **مصدر skill-creator**: [anthropics/skills — skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator)
- **وثائق مهارات Claude Code**: [anthropics/claude-code — plugin-dev/skills](https://github.com/anthropics/claude-code/tree/main/plugins/plugin-dev/skills)
