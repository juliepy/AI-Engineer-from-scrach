[English version →](../../../en/projects/project-06-runtime-observability-and-debugging/)

> Tegishli maʼruzalar: [11-maʼruza. Agent ishining runtimeʼda kuzatilishini taʼminlang](./../../lectures/lecture-11-why-observability-belongs-inside-the-harness/index.md) · [12-maʼruza. Har bir sessiya yakunida toza holat qoldiring](./../../lectures/lecture-12-why-every-session-must-leave-a-clean-state/index.md)
> Andoza fayllari: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/templates/)

# Loyiha 06. Toʻliq agent harnessʼini quring (Capstone)

## Nima qilasiz

Bu capstone (yakunlovchi) loyihadir. Dastlabki beshta loyihada oʻrganilgan barcha narsalarni bir joyga toʻplang, toʻliq benchmark ishlating, soʻngra sifatni barqaror ushlab turish mumkinligini isbotlash uchun tozalash (cleanup) bosqichini amalga oshiring.

Toʻliq mahsulot boʻlagini (product slice) qamrab oladigan qatʼiy koʻp funksiyali (multi-feature) vazifalar toʻplamidan foydalaning: hujjatni import qilish, indekslash, iqtiboslarga asoslangan Q&A, runtime kuzatuvchanligi va oʻqish mumkin boʻlgan qayta ishga tushiriladigan (restartable) repo holati. Avval kuchsiz asosiy (baseline) harness bilan ishga tushiring, soʻngra oʻzingizning eng kuchli harnessʼingiz bilan, oxirida esa tozalash qilib, qayta ishlating. Va nihoyat, harnessʼda ablasyon (ablation) tajribasini oʻtkazing — har bir komponentni bittadan olib tashlang va haqiqatda qaysi biri muhim ekanligini aniqlang.

## Repodagi tayyor loyihadan foydalaning

Repo yoʻli: [`projects/project-06/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-06)

| Katalog | Nimalar bor | Nimani taqqoslash |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-06/starter) | Mahsulot deyarli tayyor, lekin harness ataylab zaiflashtirilgan: faqat asosiy [`AGENTS.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/starter/AGENTS.md), `feature_list.json`, `session-handoff.md`, clean-state checklist va benchmark/cleanup scripts yoʻq. | Zaif harness baselineʼini qoʻlda kuzatish. |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-06/solution) | Toʻliq harness: [`AGENTS.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/AGENTS.md), [`CLAUDE.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/CLAUDE.md), [`feature_list.json`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/feature_list.json), [`init.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/init.sh), [`session-handoff.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/session-handoff.md), [`clean-state-checklist.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/clean-state-checklist.md), quality/evaluator docs va scripts. | [`projects/project-06/solution/scripts/benchmark.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/scripts/benchmark.sh) va [`projects/project-06/solution/scripts/cleanup-scanner.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/scripts/cleanup-scanner.sh)ni ishga tushirib, quality evidenceʼni taqqoslash. |

## Vositalar

- Claude Code yoki Codex
- Git
- Node.js + Electron
- Sifat hujjati andozasi (Quality document template)
- Baholovchi rubrikasi (Evaluator rubric)
- Dastlabki beshta loyihada toʻplangan barcha harness komponentlari

## Harness mexanizmi

Toʻliq harness: barcha mexanizmlar + kuzatuvchanlik (observability) + ablasyon oʻrganish (ablation study)
