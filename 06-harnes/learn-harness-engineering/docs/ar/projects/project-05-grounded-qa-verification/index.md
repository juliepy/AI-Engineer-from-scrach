[中文版本 →](../../../zh/projects/project-05-grounded-qa-verification/)

> محاضرات مرتبطة: [المحاضرة 09. امنع الوكلاء من إعلان النجاح مبكرًا](./../../lectures/lecture-09-why-agents-declare-victory-too-early/index.md) · [المحاضرة 10. التشغيل الكامل للـ pipeline فقط يُعد تحققًا حقيقيًا](./../../lectures/lecture-10-why-end-to-end-testing-changes-results/index.md)
> ملفات القوالب: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/ar/resources/templates/)

# المشروع 05. اجعل الوكيل يتحقق من عمله

## ما الذي ستفعله

نفذ فصل الأدوار: generator ينفذ، و evaluator يراجع، وربما planner. شغّل ثلاث مرات لقياس أثر كل دور مضاف.

اختر ترقية جوهرية لميزة، مثل محادثة متعددة الأدوار، أو إعادة تصميم لوحة الاستشهادات، أو فلترة المستندات، وحافظ عليها ثابتة في كل التشغيلات.

## استخدم المشروع الموجود في المستودع

مسار المستودع: [`projects/project-05/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05)

| المجلد | ماذا يحتوي | ماذا تقارن |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/starter) | تطبيق مبني على Project 04 قبل ترقية سجل المحادثة. | نقطة البداية إذا أردت إعادة تشغيل المتغيرات الثلاثة. |
| [`solution/single-role/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/solution/single-role) | وكيل واحد يخطط وينفذ ويقيّم نفسه. | الدرجة والعيوب في [`evaluator-rubric.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/single-role/evaluator-rubric.md). |
| [`solution/gen-eval/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/solution/gen-eval) | generator + evaluator مع دليل مراجعة. | الدرجة وملاحظات revision في [`evaluator-rubric.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/gen-eval/evaluator-rubric.md). |
| [`solution/plan-gen-eval/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/solution/plan-gen-eval) | planner + generator + evaluator مع sprint contract. | [`sprint-contract.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/plan-gen-eval/sprint-contract.md) ودليل الدرجة الأعلى في [`evaluator-rubric.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/plan-gen-eval/evaluator-rubric.md). |

## الأدوات

- Claude Code أو Codex
- Git
- Node.js + Electron

## آلية harness

تحقق ذاتي + Q&A مستند إلى أدلة + إكمال مبني على الدليل
