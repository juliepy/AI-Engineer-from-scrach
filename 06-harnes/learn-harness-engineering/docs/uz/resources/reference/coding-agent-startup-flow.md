# Kod yozuvchi agentni ishga tushirish oqimi (Coding Agent Startup Flow)

Inisializatsiya yakunlangandan keyin, har bir sessiyaning boshida ushbu oqimdan foydalaning.

## Belgilangan ishga tushish andozasi (Fixed Startup Template)

1. `pwd` buyrugʻini ishga tushiring va repozitoriyning asosiy (root) jildidaligini tasdiqlang.
2. `claude-progress.md` faylini oʻqing.
3. `feature_list.json` faylini oʻqing.
4. `git log --oneline -5` orqali oxirgi commitlarni koʻrib chiqing.
5. `./init.sh` skriptini ishlating.
6. Bazaviy smoke test yoki end-to-end oqimini tekshiring.
7. Agar bazaviy holat (baseline) buzilgan boʻlsa, avvalo uni tuzating.
8. Tugallanmaganlar ichidan eng yuqori ustuvorlikka ega funksiyani (feature) tanlang.
9. Toki tekshiruvdan (verified) oʻtmaguncha yoki tasdiqlangan holda toʻsilmaguncha (blocked) faqat oʻsha funksiya ustida ishlang.

## Nima uchun bu ketma-ketlik muhim

- `pwd` notoʻgʻri katalogda tasodifan ishlab qoʻyishni oldini oladi.
- progress va feature fayllari yangi tahrirlar boshlanishidan oldin barqaror holatni (durable state) tiklab beradi.
- oxirgi commitlar yaqinda nima oʻzgarganini tushuntiradi.
- `init.sh` xotiraga tayanish oʻrniga oʻrnatishni (setup) standartlashtiradi.
- bazaviy tekshiruv (baseline verification) yangi yozilgan kodlar uni yashirib qoʻyishidan oldinroq mavjud buzilgan holatlarni tutadi.

## Sessiya yakunidagi oyna (End-Of-Session Mirror)

Sessiya xuddi shu tarzda quyidagilar bilan yakunlanishi kerak:

1. jarayonni (progress) yozib qoldirish
2. funksiya (feature) holatini yangilash
3. zarur boʻlsa topshirish xatini (handoff) yozish
4. xavfsiz (buzilmagan) ishlarni commit qilish
5. toza qayta ishga tushirish yoʻlini (clean restart path) qoldirish
