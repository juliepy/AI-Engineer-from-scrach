[English version →](../../../en/projects/project-04-incremental-indexing/)

> Tegishli maʼruzalar: [7-maʼruza. Agentlar uchun aniq vazifa chegaralarini chizing](./../../lectures/lecture-07-why-agents-overreach-and-under-finish/index.md) · [8-maʼruza. Agent nima qilishini cheklash uchun funksiyalar roʻyxatidan foydalaning](./../../lectures/lecture-08-why-feature-lists-are-harness-primitives/index.md)
> Andoza fayllari: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/templates/)

# Loyiha 04. Agent harakatlarini toʻgʻrilash uchun Runtime qayta aloqadan foydalaning

## Nima qilasiz

Qatlamlararo qoidabuzilishlarning (cross-layer violations) oldini olish uchun runtime kuzatuvchanligini (ishga tushish loglari, import/indekslash loglari, xatolik holatlari) va arxitektura cheklovlarini qoʻshing. Agent toʻgʻrilashi uchun runtime bug qoldiring.

Siz buni ikki marta bajarasiz: birinchisida loglar va cheklovlarsiz, ikkinchisida tegishli vositalar va qoidalar bilan.

## Repodagi tayyor loyihadan foydalaning

Repo yoʻli: [`projects/project-04/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-04)

| Katalog | Nimalar bor | Nimani taqqoslash |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-04/starter) | Project 03 kodi, diagnostika signallari zaif. Kiritilgan indexing nuqsoni katta fayllar chunkingʼini buzishi mumkin; architecture check script yoʻq. | Runtime signallarsiz agent root causeʼni qancha vaqtda topadi. |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-04/solution) | Structured logger, architecture boundary hujjatlari va script, tuzatilgan chunking logic, [`clean-state-checklist.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/clean-state-checklist.md). | Logs va boundary checks tuzatishni tezroq va kamroq xavfli qiladimi. |

Tekshiriladigan fayllar: [`projects/project-04/solution/src/services/logger.ts`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/src/services/logger.ts), [`projects/project-04/solution/scripts/check-architecture.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/scripts/check-architecture.sh), [`projects/project-04/solution/docs/ARCHITECTURE.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/docs/ARCHITECTURE.md), [`projects/project-04/solution/src/services/indexing-service.ts`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/src/services/indexing-service.ts).

## Vositalar

- Claude Code yoki Codex
- Git
- Node.js + Electron

## Harness mexanizmi

Runtime qayta aloqa (Runtime feedback) + skoup nazorati (scope control) + bosqichma-bosqich indekslash (incremental indexing)
