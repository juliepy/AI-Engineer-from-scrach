# SOP: Chrome DevTools Validatsiya Sikli (Validation Loop)

UI ishlarini bajarishda foydalanuvchining runtime (ishlash) davomidagi harakatlariga va skrinshotlarga tayanilganda, hamda shunchaki kodni tekshirishdan koʻra DOM holati va console natijalari muhimroq boʻlganda, ushbu SOP (Standard Operating Procedure) dan foydalaning.

## Maqsad

UI validatsiyasini (tekshiruvini) agent qayta-qayta ishga tushira oladigan, va toki jarayon (journey) toza va xatosiz oʻtmaguncha takrorlanadigan ketma-ketlikka aylantirish.

## Asosiy Sikl (Core Loop)

1. Maqsad qilingan sahifa (page) yoki ilovani (app instance) tanlash.
2. Consoleʼdagi eskirgan (stale) shovqinlarni (loglarni) tozalash.
3. OLDINGI (BEFORE) holatni yozib olish (capture).
4. UI yoʻlini (path) ishga tushirish.
5. Harakatlanish davrida yuz bergan runtime hodisalarini (events) kuzatish.
6. KEYINGI (AFTER) holatni yozib olish.
7. Tuzatish kiritish va zarur boʻlsa ilovani qayta ishga tushirish.
8. Jarayon mutlaqo toza (clean) boʻlgunicha validatsiyani qayta ishga tushirish.

## Talab qilinadigan Kiritmalar (Inputs)

- barqaror ishga tushirish (startup) buyrugʻi
- qayta ishga tushirib koʻrsa boʻladigan (reproducible) UI jarayoni (journey)
- DOM, console yoki skrinshotlarning holatini suratga (snapshot) olib olish imkoniyati
- “Toza” (clean) deganda nima nazarda tutilganligining qoidasi

## Bajarish SOPʼi (Execution SOP)

1. Rejalashtirilayotgan maqsadli jarayonni (target journey) faol rejaga yozing.
2. Kuzatiladigan atamalarda nima muvaffaqiyat hisoblanishini yozing: matn koʻrinmoqda, tugma faollashgan (enabled), xato (error) yoʻqolgan, console toza, soʻrov (request) muvaffaqiyatli oʻtgan.
3. Foydalanuvchi taʼsirigacha boʻlgan (before interaction) dastlabki holatni yozib (snapshot) oling.
4. Bir vaqtning oʻzida aynan bitta yoʻlni (path) ishga tushiring.
5. Runtime hodisalarini, DOM oʻzgarishlarini va koʻrinadigan natijalarni yozib oling.
6. Agar jarayon (journey) muvaffaqiyatsiz boʻlsa, xatoga sabab boʻlgan eng kichik qatlamni (layer) toʻgʻrilang va qayta ishga tushiring (restart).
7. Xuddi shu yoʻlni qayta ishga tushiring va OLDINGI (BEFORE)/KEYINGI (AFTER) dalillarini taqqoslang.

## Tozalik Mezonlari (Clean Criteria)

- maqsad qilingan (intended) vizual holat koʻrinib turibdi
- kutilmagan xatolar (unexpected errors) yoʻq
- consoleʼdagi shovqinlarning (noise) sababi aniq yoki tozalangan
- aynan shu yoʻlni (path) qayta ishga tushirish aynan bir xil natija beradi

## Yangilanishi Kerak Boʻlgan Repo Artefaktlari

- faol ijro etish (execution) rejasi
- agar jarayon “oltin yoʻl” (golden path - ideal holat) ga aylansa `docs/RELIABILITY.md`
- agar vizual xulq-atvor (visible behavior) oʻzgargan boʻlsa mahsulot tavsifi (product spec)
