# AGENTS.md

Bu depo, uzun süreli kod yazma ajanı çalışması için tasarlanmıştır. Amaç,
ham kod çıktısını en üst seviyeye çıkarmak değildir. Amaç, depoyu, bir sonraki
oturumun tahmin yürütmeden devam edebileceği bir durumda bırakmaktır.

## Başlatma İş Akışı

Kod yazmadan önce:

1. Çalışma dizinini `pwd` ile doğrulayın.
2. En son doğrulanmış durum ve sıradaki adım için `claude-progress.md` dosyasını okuyun.
3. `feature_list.json` dosyasını okuyun ve en yüksek öncelikli, bitmemiş özelliği seçin.
4. Son commit'leri `git log --oneline -5` ile inceleyin.
5. `./init.sh` komutunu çalıştırın.
6. Yeni işe başlamadan önce gerekli duman (smoke) veya uçtan uca doğrulamayı çalıştırın.

Temel doğrulama zaten başarısız oluyorsa, önce bunu düzeltin. Bozuk bir
başlangıç durumunun üzerine yeni özellik işi yığmayın.

## Çalışma Kuralları

- Aynı anda yalnızca bir özellik üzerinde çalışın.
- Sadece kod eklendi diye bir özelliği tamamlandı olarak işaretlemeyin.
- Bir engelleyici, dar kapsamlı bir destek düzeltmesi gerektirmediği sürece
  değişiklikleri seçilen özelliğin kapsamı içinde tutun.
- Uygulama sırasında doğrulama kurallarını sessizce değiştirmeyin.
- Sohbet özetleri yerine kalıcı depo dosyalarını tercih edin.

## Gerekli Dosyalar

- `feature_list.json`: özellik durumunun doğruluk kaynağı
- `claude-progress.md`: oturum günlüğü ve mevcut doğrulanmış durum
- `init.sh`: standart başlatma ve doğrulama yolu
- `session-handoff.md`: daha büyük oturumlar için isteğe bağlı, derli toplu devir

## Bitti Tanımı

Bir özellik yalnızca aşağıdakilerin tümü doğruysa tamamlanmış sayılır:

- hedeflenen davranış uygulandı
- gerekli doğrulama gerçekten çalıştırıldı
- kanıt `feature_list.json` veya `claude-progress.md` dosyasında kayıt altına alındı
- depo standart başlatma yolundan yeniden başlatılabilir durumda kalıyor

## Oturum Sonu

Bir oturumu bitirmeden önce:

1. `claude-progress.md` dosyasını güncelleyin.
2. `feature_list.json` dosyasını güncelleyin.
3. Çözülmemiş riskleri veya engelleyicileri kaydedin.
4. İş güvenli bir duruma geldiğinde açıklayıcı bir mesajla commit edin.
5. Sıradaki oturumun anında `./init.sh` çalıştırabileceği kadar temiz bir depo
   bırakın.
