[中文版本 →](../../../zh/projects/project-03-multi-session-continuity/)

> محاضرات مرتبطة: [المحاضرة 05. حافظ على السياق حيًا عبر الجلسات](./../../lectures/lecture-05-why-long-running-tasks-lose-continuity/index.md) · [المحاضرة 06. هيئ قبل كل جلسة وكيل](./../../lectures/lecture-06-why-initialization-needs-its-own-phase/index.md)
> ملفات القوالب: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/ar/resources/templates/)

# المشروع 03. أبقِ الوكيل يعمل بعد إعادة تشغيل الجلسات

## ما الذي ستفعله

أضف تحكمًا في النطاق وبوابات تحقق إلى الوكيل. نفذ تقسيم المستندات، واستخراج metadata، وعرض تقدم الفهرسة، وتدفق Q&A قائم على الاستشهادات. استخدم `feature_list.json` لتتبع حالة الميزات: ميزة واحدة كل مرة، ولا تضع `pass` دون دليل تحقق.

ستنفذه مرتين: الأولى دون قيود، والثانية مع تطبيق صارم.

## استخدم المشروع الموجود في المستودع

مسار المستودع: [`projects/project-03/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-03)

| المجلد | ماذا يحتوي | ماذا تقارن |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-03/starter) | كود Project 02 وفيه indexing و Q&A مع citations غير مكتملين بعد. يوجد [`feature_list.json`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/starter/feature_list.json) أولي، لكن لا توجد ملفات handoff/restart النهائية. | هل ينحرف الوكيل بين عدة ميزات أو يفقد الحالة بعد إعادة التشغيل. |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-03/solution) | chunking و metadata و index status و citation-based Q&A مكتملة، مع [`init.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/init.sh) و [`session-handoff.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/session-handoff.md) و [`claude-progress.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/claude-progress.md) و [`clean-state-checklist.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/clean-state-checklist.md). | هل تملك كل ميزة دليل تحقق قبل وضعها في حالة pass. |

## الأدوات

- Claude Code أو Codex
- Git
- Node.js + Electron

## آلية harness

سجل تقدم + handoff الجلسة + استمرارية متعددة الجلسات
