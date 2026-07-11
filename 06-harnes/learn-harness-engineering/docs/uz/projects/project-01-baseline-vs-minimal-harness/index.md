[English version →](../../../en/projects/project-01-baseline-vs-minimal-harness/)

> Tegishli maʼruzalar: [1-maʼruza. Kuchli modellar doim ham ishonchli degani emas](./../../lectures/lecture-01-why-capable-agents-still-fail/index.md) · [2-maʼruza. Harness aslida nima degani](./../../lectures/lecture-02-what-a-harness-actually-is/index.md)
> Andoza fayllari: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/templates/)

# Loyiha 01. Prompt-only vs. rules-first: Bu qanchalik farq qiladi

## Nima qilasiz

Minimal Electron bilimlar bazasi (knowledge-base) ilovasi (app) qobigʻini quring — chap tomonda hujjatlar roʻyxati, oʻng tomonda Q&A (savol-javob) paneli va lokal maʼlumotlar katalogiga ega oyna. Vazifaning oʻzi murakkab emas. Murakkab qismi shundaki — agentga buni qanday qilib bajartirishdir.

Buni ikki marta ishga tushirasiz. Birinchi marta: hech qanday tayyorgarliksiz, faqat prompt bilan. Ikkinchi marta: repoda oldindan joylashtirilgan `AGENTS.md`, `init.sh`, `feature_list.json` bilan. Va keyin taqqoslaysiz.

Bu kurs ssenariysi qatʼiy oʻlchangan natijaga emas, balki qisqa qayta kashf qilish/tayyorgarlik oraligʻini misol sifatida oladi.

## Vositalar

- Claude Code yoki Codex (bittasini tanlang va ikkala urinish uchun ham ishlatasiz)
- Git (branchʼlarni boshqarish va taqqoslash uchun)
- Node.js + Electron (loyiha steki)
- Taymer (har bir urinish qancha vaqt olganini yozib borish uchun)

## Harness mexanizmi

Minimal harness: `AGENTS.md` + `init.sh` + `feature_list.json`

## Repoga kiritilgan loyihadan foydalaning

Repo yo‘li: [`projects/project-01/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-01)

| Katalog | Nimalar bor | Qanday ishlatish / nimani taqqoslash |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-01/starter) | Zaif harness yugurishi. Vazifa tavsifi sifatida faqat [`task-prompt.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/starter/task-prompt.md) bor, `AGENTS.md` yoki `feature_list.json` yo‘q. | Promptni agentga bering va qo‘shimcha tuzilmasiz nimalarni tugatishini o‘lchang. |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-01/solution) | Xuddi shu mahsulot kesimi, lekin aniq harness artefaktlari bilan: [`AGENTS.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/AGENTS.md), [`CLAUDE.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/CLAUDE.md), [`init.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/init.sh), [`feature_list.json`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/feature_list.json), [`claude-progress.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/claude-progress.md). | Qoidalar va tekshiruv bir xil vazifani qanday aniq va tekshiriladigan qiladi — taqqoslang. |

4 ta aniq feature: oynani ishga tushirish, hujjatlar ro‘yxati, savol paneli va lokal ma’lumotlar katalogini yaratish. Har bir feature uchun kutiladigan evidence `solution/feature_list.json`da.
