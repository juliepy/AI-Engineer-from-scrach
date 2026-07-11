<p align="center">
  <a href="README.md"><img alt="English" src="https://img.shields.io/badge/English-d9d9d9"></a>
  <a href="README-CN.md"><img alt="简体中文" src="https://img.shields.io/badge/简体中文-d9d9d9"></a>
  <a href="README-ZH-TW.md"><img alt="繁體中文" src="https://img.shields.io/badge/繁體中文-d9d9d9"></a>
  <a href="README-JA.md"><img alt="日本語" src="https://img.shields.io/badge/日本語-d9d9d9"></a>
  <a href="README-ES.md"><img alt="Español" src="https://img.shields.io/badge/Español-d9d9d9"></a>
  <a href="README-FR.md"><img alt="Français" src="https://img.shields.io/badge/Français-d9d9d9"></a>
  <a href="README-KO.md"><img alt="한국어" src="https://img.shields.io/badge/한국어-d9d9d9"></a>
  <a href="README-AR.md"><img alt="العربية" src="https://img.shields.io/badge/العربية-d9d9d9"></a>
  <a href="README-VI.md"><img alt="Tiếng_Việt" src="https://img.shields.io/badge/Tiếng_Việt-d9d9d9"></a>
  <a href="README-DE.md"><img alt="Deutsch" src="https://img.shields.io/badge/Deutsch-d9d9d9"></a>
  <a href="README-TR.md"><img alt="Türkçe" src="https://img.shields.io/badge/Türkçe-d9d9d9"></a>
</p>

# Skills

يحتوي هذا المجلد على skills قابلة لإعادة الاستخدام لوكلاء الذكاء الاصطناعي في مشروع Learn Harness Engineering. كل skill هي قالب prompt مستقل يمكن تحميله بواسطة وكلاء البرمجة مثل Claude Code وCodex وCursor وWindsurf.

## Skills المتاحة

### harness-creator

Skill لإنتاج harness engineering بجودة إنتاجية لوكلاء البرمجة. تساعد على إنشاء وتقييم وتحسين ملفات harness الخاصة بالوكيل، مثل AGENTS.md وقوائم الميزات وسير عمل التحقق وآليات استمرار الجلسة.

- **7 أنماط مرجعية**: Memory Persistence وSkill Runtime وContext Engineering وTool Registry وMulti-Agent Coordination وLifecycle & Bootstrap وGotchas
- **قوالب**: AGENTS.md/CLAUDE.md وfeature-list.json وinit.sh وprogress.md وsession-handoff.md
- **Scripts**: إنشاء scaffold، التحقق، تقرير HTML، وbenchmark بنيوي
- **10 حالات eval مدمجة**

راجع التوثيق الكامل في [harness-creator/README.md](harness-creator/README.md).

## كيف تم بناء harness-creator

تم تطوير `harness-creator` باستخدام منهجية **skill-creator**، وهي meta-skill رسمية من Anthropic لإنشاء skills للوكلاء واختبارها وتحسينها عبر مسار draft → test → evaluate → iterate.

## كيف تعمل Skills

تتبع كل skill بنية قياسية:

1. **SKILL.md** — نقطة الدخول، وتتضمن YAML frontmatter وتعليمات Markdown للوكيل.
2. **references/** — مستندات إضافية يتم تحميلها عند الحاجة.
3. **templates/** — قوالب بداية يمكن أن تولدها skill.

تستخدم skills أسلوب progressive disclosure: يرى الوكيل الاسم والوصف أولا، ثم يحمّل SKILL.md عند التفعيل، ويقرأ الموارد المرفقة فقط عند الحاجة.

## الأمان

تمت مراجعة ملفات هذا المجلد أمنيا:

- لا توجد backdoors أو URL مخفية أو payloads مشفرة
- لا يوجد تسريب بيانات أو بيانات اعتماد hardcoded
- لا توجد ثغرات command injection
- تستخدم scripts وحدات Node.js المدمجة فقط
- `init.sh` المولّد يشغل أوامر التحقق المكتشفة للمشروع

## الرخصة

MIT
