# PLANS.md

Bu dosya, yürütme planlarının nasıl oluşturulduğunu, güncellendiğini,
tamamlandığını ve arşivlendiğini tanımlar.

## Bir Plan Ne Zaman Gerekli

Çalışma şu durumlarda bir yürütme planı oluşturun:

- birden fazla oturumu kapsıyor
- birden fazla alt sistemi değiştiriyor
- önemsiz olmayan doğrulama ya da rollout riski taşıyor
- kaydedilmesi gereken açık kararlara bağlı

## Plan Konumları

- `docs/exec-plans/active/`: şu anda çalışmayı yönlendiren planlar
- `docs/exec-plans/completed/`: gelecekteki ajan bağlamı için saklanan
  biten planlar
- `docs/exec-plans/tech-debt-tracker.md`: ertelenmiş çalışma ve takipler

## Minimum Plan Bölümleri

- amaç
- kapsam ve kapsam dışı
- doğrulama yolu
- riskler ve engelleyiciler
- ilerleme günlüğü
- açık kararlar

## İşletim Kuralları

- Bir aktif planın net olarak sahiplenilmiş bir mevcut adımı olmalıdır.
- Plan iş ilerledikçe güncellenmeli; durağan bir metin gibi ele alınmamalı.
- Bir karar uygulama yönünü değiştirirse, onu plana kaydedin.
- Biten planları `completed/`'a taşıyın ki ajanlar önceki bağlamı yine de
  keşfedebilsin.
