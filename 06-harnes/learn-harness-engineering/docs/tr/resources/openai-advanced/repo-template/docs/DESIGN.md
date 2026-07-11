# DESIGN.md

Bu dosya tasarımın giriş noktasıdır. Kısa tutun ve `docs/design-docs/`
altındaki daha ayrıntılı dosyalara yönlendirmek için kullanın.

## Amaç

Tek bir sohbeti, sprint'i ya da incelemecinin hafızasını aşacak kalıcı
ürün ve sistem tasarım kararlarını kaydedin.

## Şu Durumlarda Okuyun

- mevcut tasarım felsefesine ihtiyacınız var
- yeni bir örüntü tanıtmak üzeresiniz
- hangi tasarım kararlarının kesinleştiğini ve hangilerinin hâlâ açık
  olduğunu bilmeniz gerekiyor

## Kanonik Tasarım Dokümanları

- `docs/design-docs/index.md`: kabul edilen, önerilen ve geçerliliğini
  yitirmiş dokümanların dizini
- `docs/design-docs/core-beliefs.md`: proje genelinde ajan odaklı inançlar

## Tasarım Kuralları

- Tasarım dokümanlarını küçük ve güncel tutun.
- Karar alanı başına bir doküman tercih edin.
- Bir değişiklik onlara bağımlıysa planlardan ve spec'lerden tasarım
  dokümanlarına bağlantı verin.
- Bir tasarım kuralı operasyonel olarak kritik hale gelirse, onu otomatik
  bir kontrole yükseltin ya da `ARCHITECTURE.md`'yi güncelleyin.
