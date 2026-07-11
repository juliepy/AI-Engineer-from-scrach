[中文版本 →](../../../zh/projects/project-06-runtime-observability-and-debugging/)

> Связанные лекции: [Лекция 11. Сделайте runtime агента наблюдаемым](./../../lectures/lecture-11-why-observability-belongs-inside-the-harness/index.md) · [Лекция 12. Чистый handoff в конце каждой сессии](./../../lectures/lecture-12-why-every-session-must-leave-a-clean-state/index.md)
> Файлы шаблонов: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/templates/)

# Проект 06. Соберите полноценный агентский harness (Capstone)

## Что вы делаете

Это capstone-проект. Соберите всё, чему научились в первых пяти проектах, проведите полный бенчмарк, затем сделайте проход уборки, чтобы убедиться, что качество поддерживаемое.

Используйте фиксированный набор multi-feature задач, охватывающий полный продуктовый срез: импорт документов, индексация, Q&A с цитатами, runtime-наблюдаемость и читаемое перезапускаемое состояние репозитория. Сначала запустите со слабым harness-baseline, затем с самым сильным harness, потом — уборку и повторный запуск. Наконец, проведите эксперимент с абляцией harness — убирайте по одному компоненту за раз и смотрите, какие из них реально важны.

## Используйте проект из репозитория

Путь: [`projects/project-06/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-06)

| Каталог | Что внутри | Что сравнивать |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-06/starter) | Продукт почти готов, но harness намеренно ослаблен: базовый [`AGENTS.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/starter/AGENTS.md), нет `feature_list.json`, `session-handoff.md`, clean-state checklist и benchmark/cleanup scripts. | Ручные наблюдения baseline со слабым harness. |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-06/solution) | Полный harness: [`AGENTS.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/AGENTS.md), [`CLAUDE.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/CLAUDE.md), [`feature_list.json`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/feature_list.json), [`init.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/init.sh), [`session-handoff.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/session-handoff.md), [`clean-state-checklist.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/clean-state-checklist.md), quality/evaluator docs и scripts. | Запустить [`projects/project-06/solution/scripts/benchmark.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/scripts/benchmark.sh) и [`projects/project-06/solution/scripts/cleanup-scanner.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/scripts/cleanup-scanner.sh), затем сравнить quality evidence. |

## Инструменты

- Claude Code или Codex
- Git
- Node.js + Electron
- Шаблон quality-документа
- Рубрика evaluator
- Все компоненты harness, накопленные за первые пять проектов

## Механизм harness

Полный harness: все механизмы + наблюдаемость + ablation-исследование
