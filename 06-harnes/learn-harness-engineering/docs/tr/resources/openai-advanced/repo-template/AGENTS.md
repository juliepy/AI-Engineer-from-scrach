# AGENTS.md

Bu depo uzun süreli kod yazma ajanı çalışması için optimize edilmiştir. Bu
dosyayı kısa tutun. Onu, dev bir talimat çöplüğü olarak değil, kayıt
sistemi dokümanlarına giden yönlendirme katmanı olarak kullanın.

## Başlangıç İş Akışı

Kodu değiştirmeden önce:

1. `pwd` ile depo kökünü onaylayın.
2. Mevcut sistem haritası ve sıkı bağımlılık kuralları için
   `ARCHITECTURE.md`'yi okuyun.
3. Hangi alanların veya katmanların en zayıf olduğunu görmek için
   `docs/QUALITY_SCORE.md`'yi okuyun.
4. `docs/PLANS.md`'yi okuyun, ardından üzerinde çalıştığınız aktif planı açın.
5. `docs/product-specs/` içindeki ilgili ürün spec'ini okuyun.
6. Bu depo için standart bootstrap ve doğrulama yolunu çalıştırın.
7. Temel doğrulama başarısızsa, kapsam eklemeden önce temeli onarın.

## Yönlendirme Haritası

- `ARCHITECTURE.md`: alan haritası, katman modeli, bağımlılık kuralları
- `docs/design-docs/index.md`: tasarım kararları ve çekirdek inançlar
- `docs/product-specs/index.md`: mevcut ürün davranışları ve kabul hedefleri
- `docs/PLANS.md`: plan yaşam döngüsü ve yürütme planı politikası
- `docs/QUALITY_SCORE.md`: ürün alanı ve katman sağlığı
- `docs/RELIABILITY.md`: runtime sinyalleri, kıyaslamalar ve yeniden
  başlatma beklentileri
- `docs/SECURITY.md`: sırlar, sandbox, veri ve dış eylem kuralları
- `docs/FRONTEND.md`: UI kısıtlamaları, tasarım sistemi kuralları,
  erişilebilirlik kontrolleri

## Çalışma Sözleşmesi

- Aynı anda tek bir sınırlı plan ya da özellik dilimi üzerinde çalışın.
- Çalışmayı yalnızca kod incelemesinden tamamlandı olarak işaretlemeyin;
  çalıştırılabilir kanıt gereklidir.
- Davranışı değiştirirseniz, aynı oturumda eşleşen ürün, plan ya da
  güvenilirlik dokümanlarını güncelleyin.
- Tekrarlanan inceleme geri bildirimi görüyorsanız, onu sohbette yeniden
  açıklamak yerine mekanik bir kurala, kontrole ya da linter'a yükseltin.
- Üretilmiş materyali `docs/generated/` içinde ve kaynak referansları
  `docs/references/` içinde tutun.
- Bu dosyayı büyütmek yerine küçük, güncel dokümanlar eklemeyi tercih edin.

## Bitirme Tanımı

Bir değişiklik yalnızca aşağıdakilerin hepsi doğruysa bitmiştir:

- hedef davranış uygulandı
- gerekli doğrulama gerçekten çalıştı
- kanıt ilgili plan ya da kalite dokümanından bağlandı
- etkilenen dokümanlar güncel kaldı
- depo standart başlangıç yolundan temiz biçimde yeniden başlatılabilir

## Oturum Sonu

Oturumu bitirmeden önce:

1. Aktif yürütme planını güncelleyin.
2. Herhangi bir alan veya katman anlamlı biçimde değiştiyse
   `docs/QUALITY_SCORE.md`'yi güncelleyin.
3. Ertelediyseniz yeni borcu `docs/exec-plans/tech-debt-tracker.md`'ye kaydedin.
4. Uygun olduğunda biten planları `docs/exec-plans/completed/`'a taşıyın.
5. Depoyu net bir sonraki eylemle yeniden başlatılabilir durumda bırakın.
