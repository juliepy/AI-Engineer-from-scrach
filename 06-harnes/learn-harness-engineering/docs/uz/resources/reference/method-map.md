# Uslub xaritasi (Method Map)

Ushbu jadval kod yozuvchi agentlarning uzoq davom etadigan muvaffaqiyatsizliklarini (failure modes) asosan ularni birinchi boʻlib hal qiluvchi artefakt yoki ishlash qoidalari (operating rule) bilan bogʻlaydi.

| Muvaffaqiyatsizlik rejimi (Failure mode) | Amaliyotda bu qanday koʻrinadi | Asosiy yechim | Yordamchi artefakt |
| --- | --- | --- | --- |
| Sovuq ishga tushishdagi chalkashlik (Cold-start confusion) | Yangi sessiya oʻz vaqtining asosiy qismini sozlamalar va holatni oʻrganishga sarflaydi | Repozitoriyni yagona haqiqat manbaiga (system of record) aylantiring | `claude-progress.md` |
| Skoupning yoyilib ketishi (Scope sprawl) | Agent bir nechta funksiyalarni boshlaydi va birortasini ham toza tugatmaydi | Faol ish koʻlamini (scope) cheklang | `feature_list.json` |
| Vaqtidan oldin tugatish (Premature completion) | Agent kod tahrirlangandan keyin, lekin ishlashga doir dalilsiz (runnable proof) yakunlanganini eʼlon qiladi | Tugatishni dalil bilan bogʻlang | `clean-state-checklist.md` |
| Moʻrt ishga tushish (Fragile startup) | Har bir sessiya loyihani qanday ishga tushirishni (boot) qaytadan oʻrganadi | Oʻrnatish va tekshirishni (verification) standartlashtiring | `init.sh` |
| Kuchsiz topshirish (Weak handoff) | Keyingi sessiya nima tasdiqlanganini, buzilganini yoki keyingi nima ekanini bilolmaydi | Aniq topshiriq xati (handoff) bilan tugating | `session-handoff.md` |
| Subyektiv baholash | Sifatni baholash did yoki xotiraga tayanib qoladi | Natijalarni belgilangan kategoriyalar boʻyicha baholang | `evaluator-rubric.md` |

## Ishlash tamoyili (Operating Principle)

Kuzatilgan muvaffaqiyatsizlik (failure mode) ni bevosita hal qiladigan eng kichik artefaktni qoʻshing. Barcha ishonchlilik muammolarini bitta global yoʻriqnoma fayliga juda koʻp matn tiqish orqali hal qilishdan qoching.
