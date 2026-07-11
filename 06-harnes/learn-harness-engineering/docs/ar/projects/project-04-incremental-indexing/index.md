[中文版本 →](../../../zh/projects/project-04-incremental-indexing/)

> محاضرات مرتبطة: [المحاضرة 07. ارسم حدود مهمة واضحة للوكلاء](./../../lectures/lecture-07-why-agents-overreach-and-under-finish/index.md) · [المحاضرة 08. استخدم قوائم الميزات لتقييد ما يفعله الوكيل](./../../lectures/lecture-08-why-feature-lists-are-harness-primitives/index.md)
> ملفات القوالب: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/ar/resources/templates/)

# المشروع 04. استخدم feedback في runtime لتصحيح سلوك الوكيل

## ما الذي ستفعله

أضف قابلية ملاحظة runtime، مثل سجلات التشغيل، وسجلات الاستيراد/الفهرسة، وحالات الأخطاء، بالإضافة إلى قيود معمارية لمنع اختراق الحدود بين الطبقات. ازرع خطأ runtime ليصلحه الوكيل.

ستنفذه مرتين: الأولى دون سجلات أو قيود، والثانية بالأدوات والقواعد المناسبة.

## استخدم المشروع الموجود في المستودع

مسار المستودع: [`projects/project-04/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-04)

| المجلد | ماذا يحتوي | ماذا تقارن |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-04/starter) | كود Project 03 مع إشارات تشخيص ضعيفة. عيب indexing المزروع قد يكسر chunking للملفات الكبيرة، ولا يوجد script لفحص المعمارية. | كم يستغرق الوكيل للوصول إلى السبب الجذري بدون إشارات runtime. |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-04/solution) | structured logger، وثائق/script لحدود المعمارية، منطق chunking مصحح، و [`clean-state-checklist.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/clean-state-checklist.md). | هل تجعل logs و boundary checks الإصلاح أسرع وأقل تدخلاً. |

ملفات مهمة: [`projects/project-04/solution/src/services/logger.ts`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/src/services/logger.ts), [`projects/project-04/solution/scripts/check-architecture.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/scripts/check-architecture.sh), [`projects/project-04/solution/docs/ARCHITECTURE.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/docs/ARCHITECTURE.md), [`projects/project-04/solution/src/services/indexing-service.ts`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/src/services/indexing-service.ts).

## الأدوات

- Claude Code أو Codex
- Git
- Node.js + Electron

## آلية harness

Feedback في runtime + تحكم في النطاق + فهرسة تدريجية
