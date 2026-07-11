# SOP: Katmanlı Alan Mimarisi

Bu SOP'u, ajan sınırları sürekli ihlal ettiğinde, katmanlar arasında
mantığı tekrarladığında ya da birkaç oturum sonra incelemesi zorlaşan
kodlar ürettiğinde kullanın.

## Hedef

Alan sınırlarını yeterince açık hale getirmek ki ajanlar yapıyı sessizce
bozmadan hızlı hareket edebilsin.

## Hedef Model

Bir iş alanı içinde, bu yönlü akışı tercih edin:

`Types -> Config -> Repo -> Service -> Runtime -> UI`

Kesişen kaygılar, açık sağlayıcılar ya da adaptörler üzerinden girmelidir.
Paylaşılan utils'ler alanın dışında kalmalı ve alan mantığı biriktirmemelidir.

## Kurulum Kontrol Listesi

- Mevcut alanları `ARCHITECTURE.md` içinde tanımlayın.
- İzin verilen bağımlılık yönlerini `ARCHITECTURE.md` içinde yazın.
- Auth, telemetri ve dış API'ler gibi kesişen arayüzleri kaydedin.
- En zor mevcut sınır ihlali için bir kısa not ekleyin.
- Lint, testler ya da betiklerle mekanik olarak neyin zorunlu kılınacağına
  karar verin.

## Yürütme SOP'u

1. Uygulama biçimine dokunmadan önce kod tabanını alanlara eşleyin.
2. Her alan için izin verilen katman dizisini belirleyin.
3. Tüm kesişen kaygıları belirleyin ve onları sağlayıcılar ya da adaptörler
   üzerinden yönlendirin.
4. Belirsiz paylaşılan mantığı ya sahibi olan alana ya da gerçekten genel
   utils'lere taşıyın.
5. Kuralları `ARCHITECTURE.md` içinde belgeleyin.
6. En yüksek maliyetli ihlal için bir çalıştırılabilir korkuluk ekleyin.
7. Değişiklikten sonra kalite puanlamasını güncelleyin.

## Bitirme Tanımı

- Yeni bir ajan hangi katmanın bir değişikliğin sahibi olduğunu söyleyebilir.
- UI kodu artık doğrudan repo veya dış yan etkilere uzanmıyor.
- Kesişen kaygıların adlandırılmış giriş noktaları var.
- En az bir önemli sınır mekanik olarak uygulanıyor.

## Güncellenecek Depo Çıktıları

- `ARCHITECTURE.md`
- `docs/QUALITY_SCORE.md`
- gerekçe değiştiyse `docs/design-docs/`
- `docs/PLANS.md` ya da aktif yürütme planı
