# SOP: Görünmez Bilgiyi Depoya Kodlama

Bu SOP'u, önemli bağlam hâlâ Google Dokümanlar'da, sohbet konularında,
biletlerde ya da insanların kafasında yaşıyorken kullanın.

## Hedef

Ajanın göremediği bilgiyi kod tabanında keşfedilebilir hale getirin ki yeni
bir oturum önceki konuşmaya bel bağlamadan ona göre hareket edebilsin.

## Tetikleyici Sinyaller

- Ajan sistemin nasıl çalıştığını sormaya devam ediyor.
- İnsanlar "buna Slack'te karar verdik" ya da "X'in geçen hafta dediğini
  takip et" diyor.
- İncelemeler, depoda yazılı olmayan ürün veya güvenlik kurallarına atıfta
  bulunuyor.
- Yeni oturumlar, çoktan halledilmiş olması gereken keşif çalışmalarını
  tekrarlıyor.

## Yürütme SOP'u

1. Görünmez bilgi kaynaklarını listeleyin: dokümanlar, sohbetler, örtük
   takım kuralları, sözlü kararlar.
2. Her kaynak için sorun: bu mimari mi, ürün davranışı mı, güvenlik
   politikası mı, güvenilirlik beklentisi mi, plan bağlamı mı yoksa
   referans materyali mi?
3. Eşleşen depo çıktısına kodlayın:
   - mimari -> `ARCHITECTURE.md`
   - ürün davranışı -> `docs/product-specs/`
   - tasarım gerekçesi -> `docs/design-docs/`
   - yürütme durumu -> `docs/exec-plans/`
   - tekrarlanan dış referanslar -> `docs/references/`
   - kalite veya güvenilirlik beklentileri -> `docs/QUALITY_SCORE.md` ya da `docs/RELIABILITY.md`
4. Bulanık ifadeleri operasyonel olarak işe yarar bir dille değiştirin.
5. Bayat kopyaları kaldırın ya da artık geçerli olmadığını işaretleyin ki
   depo tek bir keşfedilebilir gerçeği korusun.

## İyi Kodlama Kuralları

- Edebi bütünlük için değil, keşfedilebilirlik için yazın.
- Açık dosya adlarıyla kısa dokümanları tercih edin.
- İlgili çıktıları birbirine bağlayın.
- Toplantı tutanaklarını değil, kalıcı kuralları saklayın.
- Depoyu, kararın verildiği aynı oturumda güncelleyin.

## Bitirme Tanımı

- Yeni bir ajan, bir insana sormadan ilgili kuralı keşfedebilir.
- Aynı gerçek, birden fazla çelişkili dosyaya dağılmış değildir.
- Yeni çıktı, yönettiği koda ya da iş akışına yakın yaşar.
