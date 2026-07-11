# FRONTEND.md

Bu fayl agentlar UI andozalarini kutilmagan tarzda (unpredictably) oʻylab topmasligi uchun frontend kutishlarini (frontend expectations) barqarorlashtiradi.

## UI Tamoyillari

- Oʻziga xoslikdan koʻra, aniqlikka va ochiqlikka (clarity) ustuvorlik bering.
- Interaktiv (interaction) oqimlarini oson topiladigan (discoverable) va qayta boshlash mumkin boʻlgan (restartable) holatda tuting.
- Bir martalik (one-off) variantlar yaratgandan koʻra, qayta ishlatiladigan sanoqli komponentlardan foydalanishni afzal koʻring.
- Foydalanish imkoniyati (Accessibility) tekshiruvlari odatiy validatsiyaning bir qismi hisoblanadi, qoʻshimcha goʻzallik emas.

## Himoya (Guardrails)

- Dizayn tizimi (design system) yoki komponentlar kutubxonasini `docs/references/` jildida hujjatlashtiring.
- Foydalanuvchiga koʻrinadigan asosiy holatlarni qayd eting: empty (boʻsh), loading (yuklanmoqda), success (muvaffaqiyat), error (xato), retry (qayta urinish).
- Matnlar, klaviatura xatti-harakatlari va vizual iyerarxiyani barcha oqimlarda bir xil saqlang.
- Qachonki UI bugʼi toʻgʻrilansa, tegishli validatsiya qadamini qoʻshing yoki yangilang.

## Validatsiya Kutilmalari (Verification Expectations)

- Eng muhim (critical) foydalanuvchi jarayonlari (user journeys) uchun dalillarni yozib oling.
- Brauzer yoki runtime validatsiya qadamlarini tegishli rejada (plan) yozib qoldiring.
- Agar vizual regressiyalar koʻp uchrasa, skrinshot yoki DOM tekshiruvlarini standartlashtiring.
