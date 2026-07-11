[中文版本 →](../../../zh/projects/project-03-multi-session-continuity/)

> Связанные лекции: [Лекция 05. Сохраняйте контекст живым между сессиями](./../../lectures/lecture-05-why-long-running-tasks-lose-continuity/index.md) · [Лекция 06. Инициализируйте перед каждой сессией агента](./../../lectures/lecture-06-why-initialization-needs-its-own-phase/index.md)
> Файлы шаблонов: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/templates/)

# Проект 03. Заставьте агента продолжать работу через перезапуски сессий

## Что вы делаете

Добавьте агенту контроль скоупа и проверочные шлюзы. Реализуйте чанкование документов, извлечение метаданных, отображение прогресса индексации и Q&A-флоу с цитатами. Используйте `feature_list.json` для отслеживания статуса фич — по одной фиче за раз, никакого «pass» без доказательств верификации.

Вы запускаете задачу дважды: первый раз — без ограничений, второй — со строгим контролем.

## Используйте проект из репозитория

Путь: [`projects/project-03/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-03)

| Каталог | Что внутри | Что сравнивать |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-03/starter) | Код Project 02, где indexing и Q&A с цитатами ещё не завершены. Есть начальный [`feature_list.json`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/starter/feature_list.json), но нет финальных файлов handoff/restart. | Теряет ли агент состояние или уходит ли в сторону между несколькими функциями. |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-03/solution) | Готовы chunking, metadata, статус index и Q&A с цитатами; есть [`init.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/init.sh), [`session-handoff.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/session-handoff.md), [`claude-progress.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/claude-progress.md), [`clean-state-checklist.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/clean-state-checklist.md). | Есть ли доказательство проверки перед отметкой функции как готовой. |

## Инструменты

- Claude Code или Codex
- Git
- Node.js + Electron

## Механизм harness

Лог прогресса + handoff между сессиями + непрерывность между сессиями
