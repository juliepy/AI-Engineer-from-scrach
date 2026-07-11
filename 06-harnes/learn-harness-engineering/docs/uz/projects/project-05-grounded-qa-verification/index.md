[English version →](../../../en/projects/project-05-grounded-qa-verification/)

> Tegishli maʼruzalar: [9-maʼruza. Agentlarni vaqtidan oldin gʻalabani eʼlon qilishdan saqlash](./../../lectures/lecture-09-why-agents-declare-victory-too-early/index.md) · [10-maʼruza. Faqatgina End-to-End testlash chinakam tekshiruvdir](./../../lectures/lecture-10-why-end-to-end-testing-changes-results/index.md)
> Andoza fayllari: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/templates/)

# Loyiha 05. Agentga oʻz ishini oʻzi tekshirishiga imkon bering

## Nima qilasiz

Rollarni ajratishni (role separation) amalga oshiring — kod yozuvchi (generator), tekshiruvchi (evaluator), hamda ixtiyoriy ravishda rejalashtiruvchi (planner). Qoʻshilgan har bir turning taʼsirini oʻlchash uchun buni uch marta ishga tushirib koʻring.

Diqqatga sazovor boʻlgan biror funksiya yangilanishini tanlang (koʻp bosqichli suhbat, iqtibos panelini qayta dizayn qilish yoki hujjatlarni filtrlash) va uni barcha urinishlar davomida bir xil qilib saqlang.

## Repodagi tayyor loyihadan foydalaning

Repo yoʻli: [`projects/project-05/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05)

| Katalog | Nimalar bor | Nimani taqqoslash |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/starter) | Project 04 asosidagi app, conversation history upgradeʼdan oldingi holat. | Uch variantni qayta ishga tushirish uchun boshlangʻich nuqta. |
| [`solution/single-role/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/solution/single-role) | Bitta agent rejalaydi, implement qiladi va oʻzini baholaydi. | [`evaluator-rubric.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/single-role/evaluator-rubric.md)dagi ball va nuqsonlar. |
| [`solution/gen-eval/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/solution/gen-eval) | Generator + evaluator, revision dalillari bor. | [`evaluator-rubric.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/gen-eval/evaluator-rubric.md)dagi ball va revision notes. |
| [`solution/plan-gen-eval/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/solution/plan-gen-eval) | Planner + generator + evaluator va sprint contract. | [`sprint-contract.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/plan-gen-eval/sprint-contract.md) hamda [`evaluator-rubric.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/plan-gen-eval/evaluator-rubric.md)dagi yuqoriroq baho dalillari. |

## Vositalar

- Claude Code yoki Codex
- Git
- Node.js + Electron

## Harness mexanizmi

Oʻz-oʻzini tekshirish (Self-verification) + asoslangan Q&A (grounded Q&A) + dalilga asoslangan tugatish (evidence-based completion)
