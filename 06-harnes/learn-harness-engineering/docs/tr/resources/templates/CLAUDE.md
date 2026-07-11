# CLAUDE.md

Uzun süreli uygulama işleri için tasarlanmış bir depoda çalışıyorsunuz.
Hızdan çok güvenilir tamamlamayı, oturumlar arası sürekliliği ve açık
doğrulamayı önceliklendirin.

## Çalışma Döngüsü

Her oturumun başında:

1. `pwd` çalıştırın ve beklenen depo kökünde olduğunuzu doğrulayın.
2. `claude-progress.md` dosyasını okuyun.
3. `feature_list.json` dosyasını okuyun.
4. Son commit'leri `git log --oneline -5` ile inceleyin.
5. `./init.sh` komutunu çalıştırın.
6. Temel duman (smoke) veya uçtan uca yolun zaten bozuk olup olmadığını kontrol edin.

Ardından bitmemiş tam bir özellik seçin ve onu doğrulayana veya neden
engellendiğini belgeleyene kadar yalnızca o özellik üzerinde çalışın.

## Kurallar

- Aynı anda tek aktif özellik.
- Çalıştırılabilir kanıt olmadan tamamlandı iddiasında bulunmayın.
- Bitmemiş işi gizlemek için özellik listesini yeniden yazmayın.
- Sadece görevi tamamlanmış göstermek için testleri kaldırmayın veya zayıflatmayın.
- Depo dosyalarını kayıt sistemi olarak kullanın.

## Gerekli Dosyalar

- `feature_list.json`
- `claude-progress.md`
- `init.sh`
- Derli toplu bir devir faydalı olduğunda `session-handoff.md`

## Tamamlama Eşiği

Bir özellik yalnızca gerekli doğrulama başarılı olduktan ve sonuç kaydedildikten
sonra `passing` durumuna geçebilir.

## Durmadan Önce

1. İlerleme günlüğünü güncelleyin.
2. Özellik durumunu güncelleyin.
3. Hâlâ bozuk veya doğrulanmamış olanı kaydedin.
4. Depo devam etmek için güvenli olduğunda commit edin.
5. Sıradaki oturum için temiz bir yeniden başlatma yolu bırakın.
