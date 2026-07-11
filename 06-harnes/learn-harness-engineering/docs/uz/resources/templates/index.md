# Andozalar boʻyicha qoʻllanma (Template Guide)

Ushbu andozalar oʻzingizning loyihangizga nusxalash uchun tayyor. Ularning har biri agentning ishlash jarayonida aniq maqsadga xizmat qiladi. Ulardagi maʼlumotlarni oʻz loyihangizning buyruqlari, fayl yoʻllari, funksiyalar (features) nomlari va tekshiruv qadamlariga moslab tahrirlang.

## Qanday boshlash kerak

Avval quyidagi toʻrtta faylni loyihangizning asosiy (root) jildiga koʻchiring:

1. `AGENTS.md` yoki `CLAUDE.md`
2. `init.sh`
3. `claude-progress.md`
4. `feature_list.json`

Qolgan fayllarni loyihangiz kattalashgani sari qoʻshib borishingiz mumkin.

---

## AGENTS.md

Asosiy (root) yoʻriqnoma fayli. Bu agent sessiya boshlaganda eng birinchi oʻqiydigan narsadir. U ishlash qoidalarini belgilaydi: kod yozishdan oldin nima qilish kerak, qanday ishlash kerak va ishni qanday tugatish kerak.

**Qanday foydalanish kerak:**

- Loyihangizning root katalogiga koʻchiring
- Ishga tushirish (startup) qadamlarini oʻz loyihangizdagi haqiqiy yoʻllar va buyruqlar bilan almashtiring
- Ish qoidalarini jamoangizning konvensiyalariga moslab tahrirlang
- “Tugatilganlik taʼrifi” (definition of done) boʻlimini saqlab qoling — bu eng muhim qismdir

**U agent uchun nima qiladi:**

- Ish boshlashdan oldin jarayon va funksiya holatini oʻqishini aytadi
- Bir vaqtning oʻzida faqat bitta funksiya ustida ishlashga majbur qiladi
- Biror narsani tugatildi deb belgilashdan oldin dalil (evidence) talab qiladi
- Toza sessiya yakuni (clean end-of-session) qanday boʻlishini taʼriflaydi

Codex yoki boshqa agentlar uchun `AGENTS.md` ishlating. Agar Claude Code bilan ishlayotgan boʻlsangiz `CLAUDE.md` ishlating — tuzilishi bir xil, faqat Claudeʼning yoʻriqnoma uslubiga moslashtirilgan.

## init.sh

Ishga tushirish skripti. Bogʻliqliklarni (dependencies) oʻrnatish, tekshirish va ishga tushirish buyrugʻini koʻrsatish — barchasi bitta urinishda.

**Qanday foydalanish kerak:**

- Loyihangizning root katalogiga koʻchiring
- Tepadagi ushbu uchta oʻzgaruvchini tahrirlang:
  - `INSTALL_CMD` — sizning kutubxonalarni oʻrnatish buyrugʻingiz (masalan, `npm install`, `pip install -r requirements.txt`)
  - `VERIFY_CMD` — bazaviy tekshiruv buyrugʻingiz (masalan, `npm test`, `pytest`)
  - `START_CMD` — dev serverni ishga tushirish buyrugʻingiz (masalan, `npm run dev`)
- Faylni bajariladigan qiling: `chmod +x init.sh`

**U nima qiladi:**

1. Joriy katalogni koʻrsatadi (agent toʻgʻri joyda ishlayotganini tasdiqlashi uchun)
2. Bogʻliqliklarni oʻrnatadi
3. Tekshiruv buyrugʻini ishga tushiradi
4. Ishga tushirish buyrugʻini koʻrsatadi (yoki agar `RUN_START_COMMAND=1` berilsa, uni bajaradi)

Agar tekshiruv yiqilsa, agent boshqa hech narsa qilishdan oldin toʻxtab, bazaviy holatni (baseline) toʻgʻrilashi kerak.

## claude-progress.md

Jarayon jurnali. Har bir sessiya ushbu faylga yozib qoldiradi va har bir yangi sessiya eng avval aynan shuni oʻqiydi.

**Qanday foydalanish kerak:**

- Loyihangizning root katalogiga koʻchiring
- “Joriy Tasdiqlangan Holat” (Current Verified State) boʻlimini loyihangiz haqidagi maʼlumotlar bilan toʻldiring
- Har bir sessiyadan soʻng, sessiya yozuvini (session record) yangilang

**Har bir maydon (field) nima anglatadi:**

- **Current Verified State** — loyiha qayerda ekanligining yagona haqiqat manbai (single source of truth)
  - `Repository root directory` — loyiha qayerda joylashgani
  - `Standard startup path` — loyihani ishga tushirish buyrugʻi
  - `Standard verification path` — testlarni ishga tushirish buyrugʻi
  - `Highest priority unfinished feature` — keyingi sessiya nima ustida ishlashi kerakligi
  - `Current blocker` — ishlarga toʻsqinlik qilayotgan narsalar
- **Session Record** — har bir sessiya uchun bitta yozuv
  - `Goal` — nima qilishni rejalashtirgan edingiz
  - `Completed` — aslida nimalar qilindi
  - `Verification run` — qanday testlar ishga tushirildi
  - `Evidence recorded` — qanday dalillar olingan
  - `Commits` — nimalar commit qilingan
  - `Known risks` — nimalar buzilgan boʻlishi ehtimoli bor
  - `Next best action` — keyingi sessiya ishni qayerdan boshlashi kerak

## feature_list.json

Funksiyalar (Feature) trekkeri. Agent amalga oshirishi kerak boʻlgan har bir funksiyaning mashina oʻqiy oladigan (machine-readable) roʻyxati, uning holati, tekshirish qadamlari va dalillari bilan.

**Qanday foydalanish kerak:**

- Loyihangizning root katalogiga koʻchiring
- Namunaviy funksiyalarni (features) oʻzingizniki bilan almashtiring
- Har bir funksiya quyidagilarni talab qiladi:
  - `id` — qisqa, takrorlanmas identifikator
  - `priority` — butun son, kichikroq = yuqoriroq ustuvorlik
  - `area` — ilovaning qaysi qismi (masalan, “chat”, “import”, “search”)
  - `title` — qisqa tavsif
  - `user_visible_behavior` — ishlaganda foydalanuvchi nimani koʻrishi kerak
  - `status` — bularning bittasi: `not_started`, `in_progress`, `blocked`, `passing`
  - `verification` — ishlashini tasdiqlash boʻyicha bosqichma-bosqich koʻrsatmalar
  - `evidence` — tekshiruvdan oʻtganining qayd etilgan dalili (agent tomonidan toʻldiriladi)
  - `notes` — boshqa ixtiyoriy kontekstlar

**Holat (Status) qoidalari:**

- `not_started` — hali tegib koʻrilmagan
- `in_progress` — ayni vaqtda ustida ishlanayotgan bitta funksiya (bir vaqtda faqat bitta)
- `blocked` — hujjatlashtirilgan muammo sababli davom ettirib boʻlmaydi
- `passing` — tekshiruvdan oʻtdi va dalil yozib qoʻyildi

Agent har qanday vaqtda `in_progress` holatida faqat bitta funksiyaga ega boʻlishi kerak.

## session-handoff.md

Sessiyalar oʻrtasida qisqacha topshirish (handoff) eslatmasi. Bir sessiya tugagach, keyingisi tezroq oʻrganib ishlashi uchun foydalaniladi.

**Qanday foydalanish kerak:**

- Loyihangizning root katalogiga koʻchiring
- Uni har bir sessiya oxirida toʻldiring (yoki agentga toʻldirtiring)

**Har bir boʻlim nimani qamrab oladi:**

- **Currently verified** — nimalar ishlayotgani tasdiqlangan va qanday tekshiruvlar ishga tushirilgan
- **Changes this session** — qanday kod yoki infratuzilma oʻzgardi
- **Still broken or unverified** — maʼlum boʻlgan muammolar va xavfli joylar
- **Next best action** — keyingi sessiya nima qilishi kerak va nimalarga tegmasligi kerak
- **Commands** — ishga tushirish, tekshirish va tezkor qidiruv uchun debug buyruqlari

Kichik sessiyalar uchun bu fayl ixtiyoriy. Ammo sessiyalar uzoq davom etganda yoki loyihada bir nechta faol joylar boʻlganda muhim hisoblanadi.

## clean-state-checklist.md

Har bir sessiyani yakunlashdan oldin tekshiriladigan nazorat roʻyxati (checklist). Repo keyingi sessiya toza holatda boshlanishi uchun yaxshi holatda qolishini taʼminlaydi.

**Qanday foydalanish kerak:**

- Loyihangizning root katalogiga koʻchiring
- Sessiyani yopishdan oldin buni birma-bir oʻqib tekshiring
- Agent ham bularni sessiyani yakunlash rutinasi sifatida tekshirishi kerak

**U nimani tekshiradi:**

- Standart startup hali ham ishlayapti
- Standart tekshiruv (verification) hali ham ishlayapti
- Jarayon jurnali (progress log) yangilangan
- Funksiyalar roʻyxati amaldagi holatni koʻrsatmoqda (yolgʻon `passing` kiritmalar yoʻq)
- Chala bajarilgan ishlar hisobotsiz tashlab ketilmagan
- Keyingi sessiya insonning qoʻlda kiritadigan tuzatishlarisiz ishlashda davom eta oladi

## evaluator-rubric.md

Agent natijalari sifatini tekshirish (review) uchun baholash qogʻozi (scorecard). Buni sessiyadan soʻng yoki loyiha bosqichlarida ish sifati talabga javob berish-bermasligini baholash uchun foydalaning.

**Qanday foydalanish kerak:**

- Loyihangizning root katalogiga koʻchiring
- Sessiyadan soʻng (yoki bir nechta sessiyadan keyin) agentning ishini 6 ta oʻlcham boʻyicha baholang
- Har bir oʻlchamga 0-2 gacha ball qoʻyiladi

**Olti oʻlcham (dimensions):**

1. **Toʻgʻrilik (Correctness)** — qilingan ish maqsad qilingan xatti-harakatlarga (behavior) mos keladimi?
2. **Tekshiruv (Verification)** — talab qilingan tekshiruvlar haqiqatda bajarilgan va dalili bormi?
3. **Skoup intizomi (Scope discipline)** — agent tanlangan funksiya chegarasidan chiqmadimi?
4. **Ishonchlilik (Reliability)** — natija restart yoki qayta ishga tushirilganda (re-run) ham ishlaydimi?
5. **Davomiylilik qulayligi (Maintainability)** — kod va hujjatlar keyingi sessiya uchun yetarlicha tushunarlimi?
6. **Topshirishga tayyorlik (Handoff readiness)** — yangi sessiya faqat repodagi artefaktlardan foydalanib davom eta oladimi?

**Xulosa variantlari:**

- Qabul qilish (Accept) — talabga javob beradi
- Qayta koʻrish (Revise) — qabul qilishdan oldin tuzatishlar kiritish kerak
- Toʻxtatish (Block) — avvalo asosiy muammolarni hal qilish kerak

**Muhim: baholovchi sozlashga muhtoj.** Avvalboshdan, agentlar oʻz-oʻzini baholashda noʻnoq (poor self-judges) — ular muammolarni koʻradi va baribir oʻzlarini-oʻzlari maqullab qabul qilishga koʻndirishadi. Siz buning ustida takror va takror ishlashingiz kerak:

1. Baholovchini (evaluator) tugatilgan bitta sprint ustida ishga tushiring.
2. Uning ballarini oʻzingizning shaxsiy (insoniy) bahoingiz bilan solishtiring.
3. Ballar farq qilgan joylarda rubrikani oʻtish/yiqilish qoidalari boʻyicha yanada aniqroq qiling.
4. Qayta ishga tushiring va mosligini (alignment) tekshiring.
5. Baholovchi sizning (odam) xulosangiz bilan doimiy mos tushmagunicha buni takrorlang.

3-5 marta sozlash aylanishlarini reja qiling. Qanday oʻzgartirishlar moslikni yaxshilaganini bilish uchun barcha oʻzgarishlarni yozib boring.

## quality-document.md

Sizning loyihangizdagi har bir mahsulot domeni va arxitektura qatlamini baholaydigan sifat koʻrinishi (quality snapshot). Faqatgina alohida sessiya natijasini emas, balki vaqt oʻtishi bilan butun kod bazasi salomatligini kuzatib boradi.

**Qanday foydalanish kerak:**

- Loyihangizning root katalogiga koʻchiring
- Sessiya boshlashdan oldin: kod bazasining qaysi joyi eng zaif ekanligini tushunish uchun uni oʻqib chiqing
- Sessiya oxirida: nima oʻzgarganiga qarab baholarni yangilang
- Vaqt oʻtishi bilan: harnessʼdagi qanday oʻzgarishlar kod salomatligini haqiqatda yaxshilaganini koʻrish uchun snapshotʼlarni solishtiring

**U nimani baholaydi:**

- **Mahsulot domenlari (Product domains)** (masalan, hujjatni import qilish, Q&A oqimi, indekslash): har bir domen tekshiruv (verification) holati, agent tushuna olishi, test barqarorligi va asosiy boʻshliqlar (gaps) boʻyicha baho (A-D) oladi
- **Arxitektura qatlamlari (Architectural layers)** (masalan, main process, preload, renderer, xizmatlar): har bir qatlam chegara (boundary) qoidalariga rioya etishi va agent tushuna olishi boʻyicha baho oladi

**Nima uchun bu muhim:**

Baholovchi rubrika (evaluator rubric) alohida agent natijalarini baholaydi. Sifat hujjati (quality document) esa butun kod bazasining oʻzini baholaydi. Ular turli xil savollarga javob beradi:

- Baholovchi rubrika: “Agent shu sessiyada yaxshi ish qildimi?”
- Sifat hujjati: “Loyiha vaqt oʻtishi bilan kuchayib boryaptimi yoki zaiflashyaptimi?”

**Qachon yangilash kerak:**

- Har bir muhim sessiyadan keyin
- Benchmarklarni taqqoslashdan oldin
- Tozalash (cleanup) yoki soddalashtirish jarayonidan keyin
- Loyihaga yangi agent yoki modelni moslashtirayotganda (onboarding)

**Harnessni soddalashtirishga aloqadorligi:**

Sifat hujjati shuningdek harnessni soddalashtirishni qoʻllab-quvvatlaydi. Har bir harness komponenti model nimalarni mustaqil bajara olmasligi haqidagi taxminlarga asoslanadi. Modellar takomillashgani sari bu taxminlar eskiradi. Biror komponentga ehtiyoj qolgan-qolmaganini tekshirish uchun:

1. Sifat hujjati snapshotʼini oling.
2. Bitta harness komponentini olib tashlang.
3. Benchmark vazifalarini ishlating.
4. Yana bir snapshot oling.
5. Taqqoslang — agar baholar tushmagan boʻlsa, u komponent ortiqcha yuk edi. Agar tushib ketsa, uni joyiga qaytaring.
