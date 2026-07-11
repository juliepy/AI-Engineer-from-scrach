# ARCHITECTURE.md

Bu dosya sistemin üst düzey haritasıdır. Kısa ve öz kalmalı, gerektiğinde
daha derin dokümanlara işaret etmelidir.

## Sistem Yapısı

- Ürün: `[ürün adıyla değiştirin]`
- Birincil kullanıcı iş akışı: `[ana iş akışıyla değiştirin]`
- Runtime yüzeyleri: `[desktop / web / cli / services / workers]`
- Ürün davranışının kayıt kaynağı: `docs/product-specs/`

## Alan Haritası

| Alan | Amaç | Birincil Giriş Noktaları | İlgili Spec |
|--------|---------|----------------------|--------------|
| `[domain-a]` | `[neye sahip]` | `[modüller / route'lar / komutlar]` | `[spec yolu]` |
| `[domain-b]` | `[neye sahip]` | `[modüller / route'lar / komutlar]` | `[spec yolu]` |

## Katman Modeli

Ajanların ad hoc mimari uydurmaması için sabit bir yönlü model kullanın:

`Types -> Config -> Repo -> Service -> Runtime -> UI`

Kesişen kaygılar, doğrudan katmanlar arasına uzanmak yerine açık sağlayıcı
ya da adaptör sınırları üzerinden girmelidir.

## Sıkı Bağımlılık Kuralları

- Alt katmanlar üst katmanlara bağımlı olmamalıdır.
- UI runtime ya da servis sözleşmelerini atlamamalıdır.
- Veri erişimi repository'ler ya da eşdeğer adaptörler üzerinden girmelidir.
- Paylaşılan yardımcılar genel kalmalı ve alan mantığı biriktirmemelidir.
- Yeni bağımlılıklar eşleşen planda ya da tasarım dokümanında gerekçelendirilmelidir.

## Kesişen Arayüzler

| Kaygı | Onaylı Sınır | Notlar |
|--------|-------------------|-------|
| Loglama ve izleme | `[sağlayıcı / yardımcı yolu]` | `[yalnızca yapılandırılmış, ad hoc console kullanımı yok]` |
| Auth | `[sağlayıcı yolu]` | `[token/oturum kuralları]` |
| Dış API'ler | `[client veya sağlayıcı yolu]` | `[rate limit / retry rehberi]` |
| Feature flag'ler | `[flag sınırı]` | `[sahiplik]` |

## Mevcut Sıcak Noktalar

- `[ajanların güvenli biçimde değiştirmesi en zor olan alan]`
- `[zayıf sınırlara ya da kırılgan testlere sahip alan]`

## Değişiklik Kontrol Listesi

Mimariyle ilgili koda dokunduğunuzda:

1. Alan haritası ya da izin verilen sınırlar değiştiyse bu dosyayı güncelleyin.
2. Gerekçe değiştiyse `docs/design-docs/` içindeki ilgili tasarım dokümanını güncelleyin.
3. Kural mekanik olarak uygulanmalıysa çalıştırılabilir bir kontrol ekleyin ya da güncelleyin.
