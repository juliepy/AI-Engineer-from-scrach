# SOP: Chrome DevTools Doğrulama Döngüsü

Bu SOP'u, UI çalışması gerçek runtime etkileşimine bağlı olduğunda ve ekran
görüntüleri, DOM durumu ile konsol çıktısı tek başına kod incelemesinden
daha önemli olduğunda kullanın.

## Hedef

UI doğrulamasını, ajanın yolculuk temizlenene kadar çalıştırabileceği
tekrarlanabilir bir etkileşim döngüsüne dönüştürmek.

## Çekirdek Döngü

1. Hedef sayfayı ya da uygulama örneğini seçin.
2. Bayatlamış konsol gürültüsünü temizleyin.
3. ÖNCE durumunu yakalayın.
4. UI yolunu tetikleyin.
5. Etkileşim sırasında runtime olaylarını gözlemleyin.
6. SONRA durumunu yakalayın.
7. Düzeltmeyi uygulayın ve gerekirse uygulamayı yeniden başlatın.
8. Yolculuk temizlenene kadar doğrulamayı yeniden çalıştırın.

## Gerekli Girdiler

- istikrarlı bir başlangıç komutu
- tekrar üretilebilir bir UI yolculuğu
- DOM, konsol ya da ekran görüntülerini yakalama yolu
- "temiz" sayılan şeyin kuralı

## Yürütme SOP'u

1. Hedef yolculuğu aktif planda yazın.
2. Başarıyı gözlemlenebilir terimlerle tanımlayın: metin mevcut, düğme
   etkin, hata gitmiş, konsol temiz, istek başarılı.
3. Etkileşimden önce başlangıç durumunun anlık görüntüsünü alın.
4. Her seferde tam olarak bir yolu tetikleyin.
5. Runtime olaylarını, DOM değişikliklerini ve görünür çıktıyı kaydedin.
6. Yolculuk başarısız olursa, sorumlu en küçük katmanı düzeltin ve yeniden başlatın.
7. Aynı yolu yeniden çalıştırın ve ÖNCE/SONRA kanıtlarını karşılaştırın.

## Temiz Kriterleri

- amaçlanan görünür durum mevcut
- beklenmeyen hatalar yok
- konsol gürültüsü anlaşılmış ya da temizlenmiş
- aynı yolu yeniden çalıştırmak aynı sonucu veriyor

## Güncellenecek Depo Çıktıları

- aktif yürütme planı
- yolculuk altın bir yola dönüşürse `docs/RELIABILITY.md`
- görünür davranış değiştiyse ürün spec'i
