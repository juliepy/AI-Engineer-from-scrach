[中文版本 →](../../../zh/projects/project-02-agent-readable-workspace/)

> Связанные лекции: [Лекция 03. Сделайте репозиторий единственным источником истины](./../../lectures/lecture-03-why-the-repository-must-become-the-system-of-record/index.md) · [Лекция 04. Разделите инструкции по файлам](./../../lectures/lecture-04-why-one-giant-instruction-file-fails/index.md)
> Файлы шаблонов: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/templates/)

# Проект 02. Сделайте проект читаемым и продолжите с того места, где остановились

## Что вы делаете

Добавьте «читаемость» в репозиторий, чтобы новый агент мог быстро понять структуру проекта, узнать текущий прогресс и продолжить работу. Конкретно: реализуйте импорт документов, просмотр деталей документа и локальное хранение, выполнив всё за две сессии.

Вы запускаете задачу дважды: первый раз — без какой-либо помощи, второй — с заранее размещёнными в репозитории `ARCHITECTURE.md`, `PRODUCT.md` и `session-handoff.md`.

## Используйте проект из репозитория

Путь: [`projects/project-02/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-02)

| Каталог | Что внутри | Что сравнивать |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-02/starter) | Код Project 01, где импорт документов, детальная страница и persistence ещё не завершены. Документация есть, но она тоньше, и нет `session-handoff.md`. | Сколько контекста второй сессии агента приходится открывать заново. |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-02/solution) | Тот же срез продукта завершён; документы для передачи состояния находятся в [`projects/project-02/solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-02/solution), также есть [`feature_list.json`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-02/solution/feature_list.json) и [`session-handoff.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-02/solution/session-handoff.md). | Может ли новая сессия продолжить работу только по состоянию репозитория. |

## Инструменты

- Claude Code или Codex
- Git
- Node.js + Electron

## Механизм harness

Воркспейс, читаемый агентом + персистентные файлы состояния
