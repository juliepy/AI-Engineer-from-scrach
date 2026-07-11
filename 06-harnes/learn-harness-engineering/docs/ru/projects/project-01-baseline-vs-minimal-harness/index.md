[中文版本 →](../../../zh/projects/project-01-baseline-vs-minimal-harness/)

> Связанные лекции: [Лекция 01. Сильные модели не означают надёжного выполнения](./../../lectures/lecture-01-why-capable-agents-still-fail/index.md) · [Лекция 02. Что на самом деле такое harness](./../../lectures/lecture-02-what-a-harness-actually-is/index.md)
> Файлы шаблонов: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/templates/)

# Проект 01. Только промпт vs. правила в первую очередь: насколько велика разница

## Что вы делаете

Соберите минимальный каркас Electron-приложения базы знаний — окно со списком документов слева, панелью Q&A справа и локальной директорией данных. Сама задача несложная. Сложно — заставить агента её выполнить.

Вы запускаете её дважды. Первый раз: только промпт, без подготовки. Второй раз: `AGENTS.md`, `init.sh`, `feature_list.json` уже размещены в репозитории. Затем сравниваете.

Этот сценарий курса использует короткий интервал повторного исследования/подготовки как пример, а не как фиксированный измеренный результат.

## Инструменты

- Claude Code или Codex (выберите один, используйте для обоих запусков)
- Git (управление ветками и сравнение)
- Node.js + Electron (стек проекта)
- Таймер (фиксируйте длительность каждого запуска)

## Механизм harness

Минимальный harness: `AGENTS.md` + `init.sh` + `feature_list.json`

## Используйте проект, уже добавленный в репозиторий

Путь в репозитории: [`projects/project-01/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-01)

| Каталог | Что внутри | Как использовать / что сравнивать |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-01/starter) | Запуск со слабым harness. Есть только [`task-prompt.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/starter/task-prompt.md) как описание задачи, без `AGENTS.md` и `feature_list.json`. | Дайте агенту prompt и измерьте, что он выполнит без дополнительной структуры. |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-01/solution) | Тот же срез продукта с явными harness-артефактами: [`AGENTS.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/AGENTS.md), [`CLAUDE.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/CLAUDE.md), [`init.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/init.sh), [`feature_list.json`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/feature_list.json), [`claude-progress.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/claude-progress.md). | Сравните, как правила и проверка делают ту же задачу конкретной и проверяемой. |

Четыре конкретные фичи: запуск окна, список документов, панель вопросов и ответов, создание локального каталога данных. Смотрите `solution/feature_list.json` для ожидаемых доказательств по каждой фиче.
