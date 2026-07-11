# OpenAI İleri Düzey Paketi

Bu klasör, OpenAI'ın "Harness engineering: leveraging Codex in an
agent-first world" yazısında anlatılan daha görüş sahibi depo yapısını
kopyalamaya hazır başlangıç dosyaları halinde paketler.

Bu paketi, minimal harness artık yeterli olmadığında ve deponuzun
aşağıdakilere ihtiyaç duyduğunda kullanın:

- kısa, yönlendirme tarzı bir `AGENTS.md`
- depo içinde kalıcı kayıt sistemi dokümanları
- aktif ve tamamlanmış yürütme planları
- açık ürün, güvenilirlik, güvenlik ve frontend politika dosyaları
- ürün alanına ve mimari katmana göre kalite puanlaması
- model dostu referans materyali klasörleri
- mimari, bilgi yakalama ve runtime doğrulama için standart işletim prosedürleri

## Dahil Edilen Başlangıç Düzeni

[`repo-template/`](./repo-template/index.md) altındaki başlangıç paketi
aşağıdaki yapıyı yansıtır:

```text
AGENTS.md
ARCHITECTURE.md
docs/
├── design-docs/
│   ├── index.md
│   └── core-beliefs.md
├── exec-plans/
│   ├── active/
│   ├── completed/
│   └── tech-debt-tracker.md
├── generated/
│   └── db-schema.md
├── product-specs/
│   ├── index.md
│   └── new-user-onboarding.md
├── references/
│   ├── design-system-reference-llms.txt
│   ├── nixpacks-llms.txt
│   └── uv-llms.txt
├── DESIGN.md
├── FRONTEND.md
├── PLANS.md
├── PRODUCT_SENSE.md
├── QUALITY_SCORE.md
├── RELIABILITY.md
└── SECURITY.md
```

## Nasıl Benimsersiniz

1. Deponuz hâlâ küçükse minimal paketten başlayın.
2. Daha güçlü bir yapıya ihtiyaç duyduğunuzda [`repo-template/`](./repo-template/index.md)
   içindeki dosyaları kendi deponuza kopyalayın.
3. `AGENTS.md`'yi kısa tutun. Onu derin dokümanlara giden bir yönlendirici
   olarak ele alın, bir ansiklopedi olarak değil.
4. Kalite, güvenilirlik ve plan dokümanlarını ayrı bir temizlik günü olarak
   değil, normal işin parçası olarak güncelleyin.
5. Üretilmiş çıktıları ve dış referansları açık tutun ki ajanlar sohbet
   geçmişine bel bağlamadan onları bulabilsin.

## SOP Kütüphanesi

[`sops/`](./sops/index.md) klasörü, yazıdaki diyagramları adım adım işletim
prosedürlerine dönüştürür:

- katmanlı alan mimarisi kurulumu
- görünmez bilgiyi depoya kodlama
- yerel gözlemlenebilirlik yığını ve geri bildirim hattı akışı
- UI çalışmaları için Chrome DevTools doğrulama döngüsü

## Tasarım İlkeleri

- Kısa giriş noktası, derin bağlantılı dokümanlar
- Kayıt sistemi olarak depo
- Mekanik kontroller, hatırlanan kuralları yener
- Planlar ve kalite geçmişi kodun yanında yaşar
- Temizlik ve sadeleştirme birinci sınıf sorumluluklardır

Bu paket bilinçli olarak görüş sahibidir, ancak yine de körü körüne
kopyalanmak yerine projenize uyarlanmalıdır.
