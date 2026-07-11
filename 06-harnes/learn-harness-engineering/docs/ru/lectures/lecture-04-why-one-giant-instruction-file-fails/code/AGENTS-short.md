# AGENTS.md

## Начните здесь (Start Here)

- Прочитайте `docs/ARCHITECTURE.md`
- Прочитайте `docs/PRODUCT.md`
- Используйте `npm run dev` для запуска приложения
- Используйте `npm run check` перед тем как пометить работу как завершённую

## Строгие правила (Hard Rules)

- Не изменяйте границы main/preload/renderer процесса Electron без
  прочтения `docs/ARCHITECTURE.md`
- Не помечайте функцию как завершённую без проверки (verification)
- Оставляйте чистое состояние (clean state) для следующей сессии
