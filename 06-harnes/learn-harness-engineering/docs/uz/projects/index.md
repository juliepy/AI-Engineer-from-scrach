# Loyihalarga xush kelibsiz

Bu Learn Harness Engineering kursining amaliyot qismidir. Faqat maʼruzalarni oʻqish yetarli emas — muhitlarni oʻzingiz qurishingiz va turli qoidalar ostida Codex, Claude Code yoki boshqa AI agentlar qanday harakat qilishini kuzatishingiz kerak.

## Loyiha xulosasi

Ushbu kurs 6 ta bosqichma-bosqich, amaliy loyihalarni oʻz ichiga oladi va ular sizga noldan boshlab qanday qilib ishonchli agent ishlash muhitini qurishni oʻrgatadi:

1. **Faqat prompt vs. Avval qoidalar (Prompt-Only vs. Rules-First)**: Agent faqat prompt bilan qanday ishlashini va minimal harness bilan qanday ishlashini taqqoslang.
2. **Agent oʻqiy oladigan ish maydoni (Agent-Readable Workspace)**: Repozitoriyni qanday qilib AI uchun qulay qilishni va ishlarni topshirish (handoff) mexanizmlarini yaratishni oʻrganing.
3. **Koʻp sessiyali uzluksizlik (Multi-Session Continuity)**: Agent ishlarni sessiyalar oʻrtasida muammosiz davom ettira olishi uchun holat fayllari va ishga tushirish (initialization) skriptlarini loyihalang.
4. **Runtime qayta aloqa va skoup nazorati (Runtime Feedback and Scope Control)**: Agentga oʻz kodini oʻzi test qilish va ishlash davomida (runtime) xatolarni tuzatish imkonini beruvchi vositalarni joriy qiling.
5. **Oʻz-oʻzini tekshirish va rollarni ajratish (Self-Verification and Role Separation)**: Gallyutsinatsiyalar va vaqtidan oldin gʻalabani eʼlon qilishning oldini olish uchun mustaqil tekshiruv mexanizmini quring.
6. **Toʻliq harness (Capstone)**: Yakuniy, kuzatiladigan (observable), end-to-end agent ish muhitini toʻplang.

## Qanday davom ettirish kerak

Har bir loyiha papkasi odatda quyidagilarni oʻz ichiga oladi:
- `starter/`: Sizning boshlangʻich ish maydoningiz (workspace).
- `solution/`: Namuna yechim (agar qiyin vaziyatga tushib qolsangiz).
- Sizning orqa foningiz va aniq maqsadlaringiz tushuntirilgan vazifa yoʻriqnomalari.

`starter/` katalogidagi vazifalarni bajarish uchun oʻzingiz afzal koʻrgan AI kod yozish agentidan (masalan, Claude Code, Cursor, Trae) foydalaning.
