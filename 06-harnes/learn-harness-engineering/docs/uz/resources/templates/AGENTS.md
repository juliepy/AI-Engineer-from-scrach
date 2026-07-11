# AGENTS.md

Ushbu repozitoriy kod yozuvchi agentlarning uzoq davom etadigan (long-running) ishlari uchun moʻljallangan. Maqsad shunchaki koʻp kod yozish emas. Maqsad reponi keyingi sessiya taxmin qilmasdan ishni davom ettira oladigan toza holatda (clean state) qoldirishdir.

## Ishga tushirish oqimi (Startup Workflow)

Kod yozishdan oldin:

1. `pwd` yordamida ish katalogini (working directory) tasdiqlang.
2. Oxirgi tasdiqlangan (verified) holat va keyingi qadamni bilish uchun `claude-progress.md` ni oʻqing.
3. `feature_list.json` faylini oʻqing va eng yuqori ustuvorlikka ega boʻlgan tugallanmagan funksiyani (feature) tanlang.
4. `git log --oneline -5` yordamida oxirgi commitlarni koʻrib chiqing.
5. `./init.sh` ni ishga tushiring.
6. Yangi ishni boshlashdan oldin talab qilinadigan smoke yoki end-to-end tekshiruvni ishga tushiring.

Agar bazaviy tekshiruv (baseline verification) allaqachon yiqilayotgan boʻlsa, avval shuni toʻgʻrilang. Buzilgan boshlangʻich holatning ustiga yangi funksiyani qurishga urinmang.

## Ishlash qoidalari (Working Rules)

- Bir vaqtning oʻzida faqat bitta funksiya ustida ishlang.
- Shunchaki kod yozilgani uchungina funksiyani tugatildi deb belgilamang.
- Toki blokirovka (blocker) majbur qilmaguncha (masalan, yordamchi tor doiradagi tuzatishga ehtiyoj tugʻilsa), oʻzgarishlarni faqat tanlangan funksiya skoupi (scope) ichida qiling.
- Ishlayotgan vaqtda (implementation) tekshirish (verification) qoidalarini jimgina oʻzgartirib qoymang.
- Chatdagi xulosalardan koʻra repodagi doimiy (durable) artefaktlarni ustun qoʻying.

## Talab qilinadigan Artefaktlar

- `feature_list.json`: funksiyalar holati (feature state) uchun yagona haqiqat manbai (source of truth)
- `claude-progress.md`: sessiya jurnali (log) va joriy tekshirilgan holat
- `init.sh`: standart ishga tushirish (startup) va tekshirish (verification) yoʻli
- `session-handoff.md`: kattaroq sessiyalar uchun topshirish xati (ixtiyoriy)

## Tugallanganlik Taʼrifi (Definition Of Done)

Funksiya quyidagilarning barchasi bajarilgandagina tugallangan deb hisoblanadi:

- moʻljallangan xatti-harakat (target behavior) toʻliq amalga oshirilgan
- talab qilingan tekshiruv (verification) haqiqatda bajarilgan
- dalillar (evidence) `feature_list.json` yoki `claude-progress.md` da yozib qoldirilgan
- repozitoriy standart ishga tushirish (startup) yoʻli orqali qayta ishga tushirishga qodir (restartable) boʻlib qolgan

## Sessiya Yakuni (End Of Session)

Sessiyani yakunlashdan oldin:

1. `claude-progress.md` ni yangilang.
2. `feature_list.json` ni yangilang.
3. Hal etilmagan xavf yoki blockerlarni (toʻsqinliklar) yozib qoldiring.
4. Ish toza (safe) holatga kelgach, tushunarli xabar bilan commit qiling.
5. Repozitoriyni keyingi sessiya toʻgʻridan-toʻgʻri `./init.sh` ni ishga tushira oladigan darajada toza qoldiring.
