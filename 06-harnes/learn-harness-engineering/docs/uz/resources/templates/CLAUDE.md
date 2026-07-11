# CLAUDE.md

Siz uzoq davom etadigan (long-running) implementatsiya (kod yozish) ishlari uchun moʻljallangan repozitoriydasiz. Tezlikdan koʻra ishonchli yakunlashga, sessiyalar oʻrtasidagi uzluksizlikka (continuity) va ishlarni isbotlashga (explicit verification) ustuvorlik bering.

## Operatsion Sikl (Operating Loop)

Har bir sessiyaning boshida:

1. `pwd` yordamida kutilgan repozitoriy root jildida (katalogida) ekanligingizni tasdiqlang.
2. `claude-progress.md` ni oʻqing.
3. `feature_list.json` faylini oʻqing.
4. `git log --oneline -5` yordamida oxirgi commitlarni koʻrib chiqing.
5. `./init.sh` ni ishga tushiring.
6. Bazaviy smoke yoki end-to-end yoʻli (path) buzilmaganligini tekshiring.

Shundan soʻng aynan bitta tugallanmagan funksiyani (feature) tanlang va uni tasdiqlamaguningizcha yoki nega toʻxtab qolganini (blocked) hujjatlashtirmaguningizcha faqat oʻsha funksiya ustida ishlang.

## Qoidalar (Rules)

- Bir vaqtning oʻzida faqat bitta funksiya faol boʻlsin.
- Ishlaydigan dalilsiz (runnable evidence) tugallanganini (completion) daʼvo qilmang.
- Chala qolgan ishlarni yashirish uchun funksiyalar roʻyxatini (feature list) qayta yozmang.
- Vazifani tugallangandek qilib koʻrsatish uchun testlarni oʻchirmang yoki yumshatmang.
- Yagona haqiqat manbai (system of record) sifatida repozitoriy artefaktlaridan foydalaning.

## Talab qilinadigan Fayllar

- `feature_list.json`
- `claude-progress.md`
- `init.sh`
- qisqacha topshirish muhim boʻlgan vaqtda `session-handoff.md`

## Tugallash Eshigi (Completion Gate)

Funksiya faqat kerakli tekshiruv (verification) muvaffaqiyatli yakunlanib va natija yozib qoʻyilgandan keyingina `passing` holatiga oʻtishi mumkin.

## Toʻxtashdan Oldin (Before You Stop)

1. Jarayon jurnalini (progress log) yangilang.
2. Funksiya (feature) holatini yangilang.
3. Hali ham buzilgan yoki tekshirilmagan (unverified) narsalarni yozib qoldiring.
4. Repozitoriy ishlashda davom etishga (resume) xavfsiz holatga kelgach, commit qiling.
5. Keyingi sessiya uchun toza qayta ishga tushirish (restart) yoʻlini qoldiring.
