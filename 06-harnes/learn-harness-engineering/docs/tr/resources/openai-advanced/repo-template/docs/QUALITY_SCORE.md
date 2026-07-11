# QUALITY_SCORE.md

Bu doküman, deponun zaman içinde güçlenip güçlenmediğini ya da
zayıflayıp zayıflamadığını izler.

## Notlandırma Ölçeği

- `A`: doğrulanmış, okunur, istikrarlı, sınırlar uygulanmış
- `B`: küçük boşluklarla çalışıyor
- `C`: kısmen çalışıyor, dikkat çekici karmaşa ya da istikrarsızlık
- `D`: bozuk, güvensiz ya da yapısal olarak belirsiz

## Ürün Alanları

| Alan | Not | Doğrulama | Ajan Okunabilirliği | Test İstikrarı | Anahtar Boşluklar | Son Güncelleme |
|--------|-------|-------------|-----------------|---------------|----------|-------------|
| `[domain-a]` | - | - | - | - | - | - |
| `[domain-b]` | - | - | - | - | - | - |
| `[domain-c]` | - | - | - | - | - | - |

## Mimari Katmanlar

| Katman | Not | Sınır Uygulaması | Ajan Okunabilirliği | Anahtar Boşluklar | Son Güncelleme |
|-------|-------|---------------------|-----------------|----------|-------------|
| Types | - | - | - | - | - |
| Services | - | - | - | - | - |
| Runtime | - | - | - | - | - |
| UI | - | - | - | - | - |

## Kıyaslama Anlık Görüntüleri

| Tarih | Harness Varyantı | Tamamlama Oranı | Yeniden Denemeler | İncelemeden Önceki Hatalar | Notlar |
|------|-----------------|----------------|--------|-----------------------|------|
| YYYY-MM-DD | `[temel / iyileştirilmiş / sadeleştirilmiş]` | - | - | - | - |

## Sadeleştirme Günlüğü

| Tarih | Kaldırılan Bileşen | Sonuç | Karar |
|------|-------------------|---------|----------|
| YYYY-MM-DD | `[bileşen]` | `[bozuldu / değişmedi]` | `[geri yükle / kaldırılmış tut]` |
