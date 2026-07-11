# SOP: Gözlemlenebilirlik Geri Bildirim Döngüsü

Bu SOP'u, hata ayıklama yavaşsa, ajanlar kanıt göstermeden başarı ilan
etmeye devam ediyorsa ya da runtime davranışını incelemek koddan daha
zorsa kullanın.

## Hedef

Ajana log'lar, metrikler, izler ve çalıştırılabilir iş yükleri üzerinde
yerel bir geri bildirim döngüsü vermek; böylece yalnızca kod incelemesinden
değil, yürütmeden de akıl yürütebilsin.

## Minimum Yığın

- uygulama yapılandırılmış log üretir
- mümkün olduğunda uygulama metrik ve izler üretir
- yerel yayın ya da toplama katmanı
- log'lar, metrikler ve izler için sorgu arayüzleri
- her değişiklikten sonra yeniden çalıştırılabilen iş yükü ya da kullanıcı
  yolculuğu

## Yürütme SOP'u

1. En çok önem taşıyan altın runtime yolculuklarını tanımlayın.
2. Başlangıca ve kritik yola yapılandırılmış log'lar ekleyin.
3. Yararlı olduğunda gecikme, hata sayısı ya da kuyruk derinliği için
   metrikler ekleyin.
4. Yavaş ya da çok adımlı akışlar için izler ya da zamanlama işaretleyicileri
   ekleyin.
5. Sinyalleri yerel geliştirme ortamından sorgulanabilir hale getirin.
6. Ajana yeniden çalıştırılabilir bir iş yükü ya da senaryo verin.
7. Döngüyü zorunlu kılın: sorgula -> ilişkilendir -> akıl yürüt -> uygula
   -> yeniden başlat -> tekrar çalıştır -> doğrula.

## Hata Ayıklama Oturumu Kontrol Listesi

- Ne başarısız oldu?
- Hangi sinyal başarısızlığı kanıtlıyor?
- Başarısızlığın sahibi hangi katman?
- Düzeltmeden sonra ne değişti?
- Uygulama temiz biçimde yeniden başladı mı?
- Aynı iş yükü yeniden çalıştırmadan sonra geçti mi?

## Bitirme Tanımı

- Ajan bir başarısızlık modunu runtime kanıtından açıklayabilir.
- Aynı iş yükü her değişiklikten sonra yeniden çalıştırılabilir.
- Yeniden başlatma ve tekrar çalıştırma normal görev döngüsünün parçasıdır.
- Güvenilirlik sinyalleri `docs/RELIABILITY.md` içinde belgelenmiştir.
