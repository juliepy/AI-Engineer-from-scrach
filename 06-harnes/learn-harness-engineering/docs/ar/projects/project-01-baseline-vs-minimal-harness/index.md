[中文版本 →](../../../zh/projects/project-01-baseline-vs-minimal-harness/)

> محاضرات مرتبطة: [المحاضرة 01. النماذج القوية لا تعني تنفيذًا موثوقًا](./../../lectures/lecture-01-why-capable-agents-still-fail/index.md) · [المحاضرة 02. ما معنى harness فعليًا](./../../lectures/lecture-02-what-a-harness-actually-is/index.md)
> ملفات القوالب: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/ar/resources/templates/)

# المشروع 01. Prompt فقط مقابل القواعد أولًا: ما حجم الفرق؟

## ما الذي ستفعله

ابنِ هيكلًا بسيطًا لتطبيق معرفة باستخدام Electron: نافذة فيها قائمة مستندات على اليسار، ولوحة Q&A على اليمين، ومجلد بيانات محلي. المهمة نفسها ليست معقدة. المعقد هو كيف تجعل الوكيل يكملها.

ستنفذها مرتين. المرة الأولى: prompt فقط، دون تحضير. المرة الثانية: مع وضع `AGENTS.md` و `init.sh` و `feature_list.json` مسبقًا في المستودع. ثم قارن.

يستخدم سيناريو الدورة هذا فترة قصيرة من إعادة الاكتشاف/التحضير كمثال، لا كنتيجة قياس ثابتة.

## الأدوات

- Claude Code أو Codex (اختر واحدًا واستخدمه في التشغيلين)
- Git (إدارة الفروع والمقارنة)
- Node.js + Electron (حزمة المشروع)
- مؤقت (لتسجيل مدة كل تشغيل)

## آلية harness

Harness بسيط: `AGENTS.md` + `init.sh` + `feature_list.json`

## استخدم المشروع المضمَّن في المستودع

مسار المشروع في المستودع: [`projects/project-01/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-01)

| المجلد | ماذا يحتوي | كيف تستخدمه / ماذا تقارن |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-01/starter) | تشغيل الـ harness الضعيف. يحتوي فقط على [`task-prompt.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/starter/task-prompt.md) كوصف للمهمة ولا يتضمن `AGENTS.md` أو `feature_list.json`. | قدّم الـ prompt لوكيلك وقِس ما الذي ينجزه بدون أي هيكلة إضافية. |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-01/solution) | نفس جزء المنتج مع ملفات harness صريحة: [`AGENTS.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/AGENTS.md) و[`CLAUDE.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/CLAUDE.md) و[`init.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/init.sh) و[`feature_list.json`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/feature_list.json) و[`claude-progress.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/claude-progress.md). | قارن كيف تجعل القواعد والتحقق نفس المهمة قابلة للتنفيذ والقياس. |

الميزات الأربع الملموسة هي: تشغيل النافذة، قائمة المستندات، لوحة الأسئلة/الأجوبة، وإنشاء مجلد البيانات المحلي. راجع `solution/feature_list.json` لمعرفة الدليل المتوقع لكل ميزة.
