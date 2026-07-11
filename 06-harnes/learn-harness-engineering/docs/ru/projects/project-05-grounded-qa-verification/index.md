[中文版本 →](../../../zh/projects/project-05-grounded-qa-verification/)

> Связанные лекции: [Лекция 09. Не давайте агентам объявлять победу слишком рано](./../../lectures/lecture-09-why-agents-declare-victory-too-early/index.md) · [Лекция 10. Только полный прогон пайплайна считается настоящей верификацией](./../../lectures/lecture-10-why-end-to-end-testing-changes-results/index.md)
> Файлы шаблонов: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/templates/)

# Проект 05. Заставьте агента самостоятельно проверять свою работу

## Что вы делаете

Реализуйте разделение ролей — генератор, который пишет код, evaluator, который ревьюит, и опционально планировщик. Запустите трижды, чтобы измерить эффект каждой добавленной роли.

Выберите содержательную фичу-апгрейд (многоходовой диалог, редизайн панели цитирования или фильтрация документов) и удерживайте её одинаковой во всех запусках.

## Используйте проект из репозитория

Путь: [`projects/project-05/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05)

| Каталог | Что внутри | Что сравнивать |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/starter) | Приложение на базе Project 04 до добавления истории диалога. | Стартовая точка для повторного запуска трёх вариантов. |
| [`solution/single-role/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/solution/single-role) | Один агент планирует, реализует и сам себя оценивает. | Оценка и дефекты в [`evaluator-rubric.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/single-role/evaluator-rubric.md). |
| [`solution/gen-eval/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/solution/gen-eval) | Generator + evaluator с доказательствами правок. | Оценка и заметки ревизии в [`evaluator-rubric.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/gen-eval/evaluator-rubric.md). |
| [`solution/plan-gen-eval/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/solution/plan-gen-eval) | Planner + generator + evaluator со sprint contract. | [`sprint-contract.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/plan-gen-eval/sprint-contract.md) и более высокая оценка в [`evaluator-rubric.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/plan-gen-eval/evaluator-rubric.md). |

## Инструменты

- Claude Code или Codex
- Git
- Node.js + Electron

## Механизм harness

Самопроверка + Q&A с обоснованием + завершение по доказательствам
