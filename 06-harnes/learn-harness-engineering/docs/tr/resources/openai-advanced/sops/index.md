# OpenAI İleri Düzey SOP'lar

Bu SOP'lar, yazıdaki işletim örüntülerini takip edebileceğiniz ya da
uyarlayabileceğiniz somut yürütme kılavuzlarına dönüştürür.

## Dahil Edilen SOP'lar

- [`layered-domain-architecture.md`](./layered-domain-architecture.md):
  açık katmanlar ve kesişen sınırlar oluşturun
- [`encode-knowledge-into-repo.md`](./encode-knowledge-into-repo.md):
  görünmez bilgiyi sohbetlerden, dokümanlardan ve hafızadan depo içindeki
  dosyalara taşıyın
- [`observability-feedback-loop.md`](./observability-feedback-loop.md):
  ajanlara log, metrik, iz ve tekrarlanabilir bir hata ayıklama döngüsü verin
- [`chrome-devtools-validation-loop.md`](./chrome-devtools-validation-loop.md):
  UI davranışını temizlenene kadar doğrulamak için tarayıcı otomasyonu ve
  anlık görüntü kullanın

## Nasıl Kullanılır

1. Mevcut darboğazınıza uyan SOP'u seçin.
2. Eksik çıktıları ya da araçları kurmak için kontrol listesini kullanın.
3. Ortaya çıkan kuralları kopyaladığınız `repo-template/` dokümanlarına kodlayın.
4. Tekrarlanan inceleme yorumlarını kontrollere, betiklere ya da korkuluklara
   dönüştürün.

Bunlar körü körüne takip edilmek için değildir. Amaçları harness'ı daha
okunur, uygulanabilir ve tekrarlanabilir kılmaktır.
