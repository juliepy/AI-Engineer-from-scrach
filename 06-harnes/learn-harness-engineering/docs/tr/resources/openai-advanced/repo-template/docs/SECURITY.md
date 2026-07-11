# SECURITY.md

Bu dosya, ajanların tahmin etmemesi gereken güvenlik ve emniyet
kurallarını tanımlar.

## Sırlar ve Kimlik Bilgileri

- Sırları asla kaynak kodda ya da dokümanlarda sabit kodlamayın.
- Onaylı sır yükleme yollarını burada belgeleyin.
- Token'ları, API anahtarlarını ve kişisel verileri log'lardan ve ekran
  görüntülerinden redakte edin.

## Güvenilmeyen Girdi

- Dış içeriği doğrulanana kadar güvenilmez kabul edin.
- İzin verilen fetch ya da yürütme sınırlarını burada kaydedin.
- Prompt enjeksiyonu ya da komut enjeksiyonu riski mevcutsa korkuluğu
  belgeleyin.

## Dış Eylemler

- Hangi eylemlerin açık onay gerektirdiğini listeleyin.
- Ajanların varsayılan olarak çalıştırmaması gereken üretim ya da yıkıcı
  komutları kaydedin.
- Hata ayıklama ve doğrulama için sandbox güvenli iş akışlarını tercih edin.

## Bağımlılık ve İnceleme Kuralları

- Yeni bağımlılıkların aktif planda gerekçelendirilmesi gerekir.
- Güvenliğe duyarlı değişiklikler açık doğrulama adımları gerektirir.
- Tekrarlanan güvenlik incelemesi yorumları, kabile bilgisi değil,
  kontroller haline gelmelidir.
