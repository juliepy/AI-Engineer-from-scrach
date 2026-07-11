# RELIABILITY.md

Bu dosya, sistemin sağlıklı ve yeniden başlatılabilir olduğunu nasıl
kanıtladığını tanımlar.

## Standart Yollar

- Bootstrap: `[komut]`
- Doğrulama: `[komut]`
- Uygulamayı veya servisi başlat: `[komut]`
- Runtime'ı hata ayıkla veya incele: `[komut]`

## Gerekli Runtime Sinyalleri

- başlangıç ve kritik akışlar için yapılandırılmış log'lar
- anahtar servisler için sağlık kontrolleri
- mevcut olduğunda yavaş yollar için iz veya zamanlama verisi
- kurtarılabilir başarısızlıklar için kullanıcı yüzlü hata durumları

## Altın Yolculuklar

- `[yolculuk 1]`
- `[yolculuk 2]`
- `[yolculuk 3]`

Her altın yolculuğun tekrarlanabilir bir doğrulama yolu ve net
başarısızlık sinyalleri olmalıdır.

## Güvenilirlik Kuralları

- Sistem sonrasında temiz biçimde yeniden başlatılamıyorsa hiçbir özellik
  tamamlanmış sayılmaz.
- Runtime başarısızlıkları depo içindeki sinyallerden teşhis edilebilmelidir.
- Tekrarlanan bir başarısızlık modu ortaya çıkarsa, onun için bir
  kıyaslama ya da korkuluk ekleyin.
- Temizlik güvenilirliğin parçasıdır, ayrı bir kaygı değildir.
