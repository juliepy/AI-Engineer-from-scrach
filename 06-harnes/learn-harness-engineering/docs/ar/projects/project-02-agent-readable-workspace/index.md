[中文版本 →](../../../zh/projects/project-02-agent-readable-workspace/)

> محاضرات مرتبطة: [المحاضرة 03. اجعل المستودع مصدر الحقيقة الوحيد](./../../lectures/lecture-03-why-the-repository-must-become-the-system-of-record/index.md) · [المحاضرة 04. قسّم التعليمات عبر ملفات](./../../lectures/lecture-04-why-one-giant-instruction-file-fails/index.md)
> ملفات القوالب: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/ar/resources/templates/)

# المشروع 02. اجعل المشروع قابلًا للقراءة واستأنف من حيث توقفت

## ما الذي ستفعله

أضف "قابلية القراءة" إلى المستودع حتى يستطيع وكيل جديد فهم بنية المشروع بسرعة، ومعرفة التقدم الحالي، واستئناف العمل. تحديدًا: نفذ استيراد المستندات، وعرض تفاصيل المستند، والحفظ المحلي، عبر جلستين.

ستنفذه مرتين: الأولى دون مساعدة، والثانية مع وضع `ARCHITECTURE.md` و `PRODUCT.md` و `session-handoff.md` مسبقًا في المستودع.

## استخدم المشروع الموجود في المستودع

مسار المستودع: [`projects/project-02/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-02)

| المجلد | ماذا يحتوي | ماذا تقارن |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-02/starter) | كود Project 01 مع import المستندات، عرض التفاصيل، و persistence غير مكتملة بعد. توجد وثائق لكنها أخف، ولا يوجد `session-handoff.md`. | مقدار السياق الذي تحتاج الجلسة الثانية من الوكيل إلى اكتشافه من جديد. |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-02/solution) | نفس جزء المنتج مكتمل، مع وثائق handoff تحت [`projects/project-02/solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-02/solution)، بالإضافة إلى [`feature_list.json`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-02/solution/feature_list.json) و [`session-handoff.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-02/solution/session-handoff.md). | هل تستطيع جلسة جديدة المتابعة اعتمادًا على حالة المستودع فقط. |

## الأدوات

- Claude Code أو Codex
- Git
- Node.js + Electron

## آلية harness

Workspace قابل للقراءة من الوكيل + ملفات حالة دائمة
