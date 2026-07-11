[中文版本 →](../../../zh/projects/project-04-incremental-indexing/)

> Связанные лекции: [Лекция 07. Чётко обозначьте границы задач для агентов](./../../lectures/lecture-07-why-agents-overreach-and-under-finish/index.md) · [Лекция 08. Используйте списки фич, чтобы ограничивать действия агента](./../../lectures/lecture-08-why-feature-lists-are-harness-primitives/index.md)
> Файлы шаблонов: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/templates/)

# Проект 04. Используйте runtime-обратную связь, чтобы корректировать поведение агента

## Что вы делаете

Добавьте runtime-наблюдаемость (логи запуска, логи импорта/индексации, состояния ошибок) и архитектурные ограничения, чтобы предотвратить нарушения границ слоёв. Подкиньте агенту runtime-баг для исправления.

Вы запускаете задачу дважды: первый раз — без логов и ограничений, второй — с правильными инструментами и правилами.

## Используйте проект из репозитория

Путь: [`projects/project-04/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-04)

| Каталог | Что внутри | Что сравнивать |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-04/starter) | Код Project 03 со слабыми диагностическими сигналами. Встроенный дефект indexing может ломать chunking больших файлов; скрипта проверки архитектуры нет. | Как быстро агент находит причину без runtime-сигналов. |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-04/solution) | Структурированный logger, документы и скрипт архитектурных границ, исправленная логика chunking и [`clean-state-checklist.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/clean-state-checklist.md). | Помогают ли logs и проверки границ исправлять быстрее и аккуратнее. |

Ключевые файлы: [`projects/project-04/solution/src/services/logger.ts`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/src/services/logger.ts), [`projects/project-04/solution/scripts/check-architecture.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/scripts/check-architecture.sh), [`projects/project-04/solution/docs/ARCHITECTURE.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/docs/ARCHITECTURE.md), [`projects/project-04/solution/src/services/indexing-service.ts`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/src/services/indexing-service.ts).

## Инструменты

- Claude Code или Codex
- Git
- Node.js + Electron

## Механизм harness

Runtime-обратная связь + контроль скоупа + инкрементальная индексация
