[English version →](../../../en/projects/project-02-agent-readable-workspace/)

> Tegishli maʼruzalar: [3-maʼruza. Repozitoriyni yagona haqiqat manbaiga aylantiring](./../../lectures/lecture-03-why-the-repository-must-become-the-system-of-record/index.md) · [4-maʼruza. Yoʻriqnomalarni fayllar boʻylab ajrating](./../../lectures/lecture-04-why-one-giant-instruction-file-fails/index.md)
> Andoza fayllari: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/templates/)

# Loyiha 02. Loyihani oʻqishga qulay qiling va toʻxtagan joyidan davom ettiring

## Nima qilasiz

Yangi agent loyiha tuzilishini tez tushunib olishi, joriy jarayon (progress) qayerdaligini bilishi va ishni davom ettirishi uchun repoga “oʻqish qulayligi”ni (readability) qoʻshing. Aniqroq qilib aytganda: ikkita sessiya davomida hujjat import qilish, hujjat detallarini koʻrish va lokal saqlashni (local persistence) amalga oshiring.

Siz buni ikki marta bajarasiz: birinchisi hech qanday yordamsiz, ikkinchisi repoda oldindan joylashtirilgan `ARCHITECTURE.md`, `PRODUCT.md` va `session-handoff.md` fayllari bilan.

## Repodagi tayyor loyihadan foydalaning

Repo yoʻli: [`projects/project-02/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-02)

| Katalog | Nimalar bor | Nimani taqqoslash |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-02/starter) | Project 01 kodi, lekin hujjat importi, detail view va persistence hali toʻliq emas. Hujjatlar bor, ammo qisqaroq; `session-handoff.md` yoʻq. | Ikkinchi agent sessiyasi qancha kontekstni qayta topishi kerak. |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-02/solution) | Xuddi shu mahsulot kesimi tugallangan; handoff hujjatlari [`projects/project-02/solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-02/solution) ostida, shuningdek [`feature_list.json`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-02/solution/feature_list.json) va [`session-handoff.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-02/solution/session-handoff.md) bor. | Yangi sessiya faqat repo holatidan davom eta oladimi. |

## Vositalar

- Claude Code yoki Codex
- Git
- Node.js + Electron

## Harness mexanizmi

Agent oʻqiy oladigan ish maydoni (Agent-readable workspace) + doimiy holat fayllari (persistent state files)
