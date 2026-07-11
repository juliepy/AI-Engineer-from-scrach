# Kod Yazma Ajanı Başlatma Akışı

Bunu, başlatma tamamlandıktan sonra her oturumun başında kullanın.

## Sabit Başlatma Şablonu

1. `pwd` çalıştırın ve depo kökünü doğrulayın.
2. `claude-progress.md` dosyasını okuyun.
3. `feature_list.json` dosyasını okuyun.
4. Son commit'leri `git log --oneline -5` ile inceleyin.
5. `./init.sh` komutunu çalıştırın.
6. Temel bir duman (smoke) veya uçtan uca yol çalıştırın.
7. Temel yol bozuksa önce onu düzeltin.
8. En yüksek öncelikli bitmemiş özelliği seçin.
9. Yalnızca o özellik üzerinde, doğrulanana veya açıkça engellenene kadar çalışın.

## Bu Sıralama Neden Önemli

- `pwd`, yanlış dizinde kazara çalışmayı engeller.
- ilerleme ve özellik dosyaları, yeni düzenlemelere başlamadan önce kalıcı durumu kurtarır.
- son commit'ler, en yakın zamanda nelerin değiştiğini açıklar.
- `init.sh`, hafızaya güvenmek yerine başlatmayı standartlaştırır.
- temel doğrulama, yeni iş bunları gizlemeden önce bozuk başlangıç durumlarını
  yakalar.

## Oturum Sonu Yansıması

Aynı oturum şu adımlarla bitmelidir:

1. ilerlemeyi kaydederek
2. özellik durumunu güncelleyerek
3. gerektiğinde bir devir notu yazarak
4. güvenli işi commit ederek
5. temiz bir yeniden başlatma yolu bırakarak
