# Başlatıcı Ajan Oyun Kitabı

Bu oyun kitabını, artımlı özellik işine başlamadan önce, bir depodaki ilk
ciddi oturum için kullanın.

## Amaç

Sonraki oturumların; başlatma komutlarını, mevcut durumu veya görev sınırlarını
yeniden çıkarmak zorunda kalmadan davranış uygulayabilmesi için kararlı bir
çalışma yüzeyi oluşturun.

## Gerekli Çıktılar

Başlatıcı, geride en azından şu dosyaları bırakmalıdır:

- `AGENTS.md` veya `CLAUDE.md` gibi bir kök talimat dosyası
- `feature_list.json` gibi makine tarafından okunabilir bir özellik yüzeyi
- `claude-progress.md` gibi kalıcı bir ilerleme dosyası
- `init.sh` gibi bir standart başlatma yardımcısı
- Temel iskeleti yakalayan ilk güvenli commit

## Kontrol Listesi

1. Standart başlatma yolunu tanımlayın.
2. Standart doğrulama yolunu tanımlayın.
3. İlerleme günlüğünü oluşturun ve başlangıç durumunu kaydedin.
4. İşi, durumları belirtilmiş açık özelliklere ayırın.
5. İlk temiz baseline commit'i oluşturun.

## Başarı Testi

Önceki sohbet bağlamı olmayan yeni bir oturum şu soruları yanıtlayabilmelidir:

- bu depo ne yapar
- nasıl başlatılır
- nasıl doğrulanır
- ne bitmemiştir
- sıradaki en iyi adım nedir
