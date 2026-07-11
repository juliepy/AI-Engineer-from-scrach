# RELIABILITY.md

Bu fayl tizimning sogʻlom (healthy) ekanligi va qayta ishga tusha olishini (restartable) qanday isbotlashini belgilaydi.

## Standart Yoʻllar (Standard Paths)

- Boshlangʻich (Bootstrap): `[buyruq]`
- Tekshiruv (Verification): `[buyruq]`
- Ilovani yoki xizmatni ishga tushirish (Start app or service): `[buyruq]`
- Nosozliklarni qidirish yoki ishlashni tekshirish (Debug or inspect runtime): `[buyruq]`

## Talab qilinadigan Runtime signallar (Required Runtime Signals)

- startup va muhim yoʻllar (critical flows) uchun strukturaviy loglar (structured logs)
- asosiy xizmatlar uchun salomatlik tekshiruvlari (health checks)
- iloji boricha sekin ishlaydigan yoʻllar uchun treys yoki timing maʼlumotlari
- qayta tiklanadigan (recoverable) xatoliklar uchun foydalanuvchiga koʻrinadigan xato (error) holatlari

## Oltin Jarayonlar (Golden Journeys)

- `[1-jarayon]`
- `[2-jarayon]`
- `[3-jarayon]`

Har bir oltin jarayon (golden journey) oʻzining qayta-qayta ishga tushirilishi mumkin boʻlgan (repeatable) tekshiruv yoʻliga va aniq muvaffaqiyatsizlik signallariga ega boʻlishi kerak.

## Ishonchlilik Qoidalari (Reliability Rules)

- Hech qaysi funksiya agar tizim ishlagandan soʻng xatosiz qayta ishga (restart cleanly) tusha olmasa tugallangan (complete) hisoblanmaydi.
- Ish ishlash jarayonidagi (runtime) xatoliklar repo-lokal signallar asosida aniqlanishi (diagnosable) kerak.
- Agar biror qaytariladigan xatolik (repeated failure mode) yuzaga kelsa, bu uchun benchmark yoki himoya toʻsigʻi (guardrail) qoʻshing.
- Tozalash ishlari (cleanup) - ishonchlilikning bir qismidir, alohida vazifa emas.
