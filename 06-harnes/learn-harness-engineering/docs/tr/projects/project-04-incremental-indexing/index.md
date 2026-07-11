[中文版本 →](../../../zh/projects/project-04-incremental-indexing/)

> İlgili dersler: [Ders 07. Ajanlar için net görev sınırları çizin](./../../lectures/lecture-07-why-agents-overreach-and-under-finish/index.md) · [Ders 08. Ajanın yaptıklarını sınırlamak için özellik listeleri kullanın](./../../lectures/lecture-08-why-feature-lists-are-harness-primitives/index.md)
> Şablon dosyaları: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/templates/)

# Proje 04. Ajan davranışını düzeltmek için runtime geri bildirimi kullanın

## Ne Yapacaksınız

Runtime gözlemlenebilirliği (başlangıç günlükleri, içe aktarma/dizinleme günlükleri, hata durumları) ve katmanlar arası ihlalleri önlemek için mimari kısıtlar ekleyin. Ajanın düzeltmesi için bir runtime hatası yerleştirin.

Depodaki starter'da runtime bug'ı kasıtlı olarak bırakılmıştır; fakat tanılama sinyali zayıftır ve mimari kontrol betiği yoktur. Solution yapılandırılmış loglar, mimari kurallar ve düzeltilmiş parçalama mantığı ekler. Runtime geri bildiriminin düzeltme kalitesini nasıl etkilediğini karşılaştırın.

İki kez çalıştırın: ilk seferinde günlükler veya kısıtlar olmadan, ikinci seferinde uygun araçlar ve kurallarla.

## Depodaki projeyi kullanın

Depo yolu: [`projects/project-04/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-04)

| Dizin | İçerik | Nasıl kullanılır |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-04/starter) | Project 03 kodu; tanılama sinyali zayıftır. Gömülü indexing hatası büyük dosya parçalamayı bozar ve mimari kontrol betiği yoktur. | Runtime sinyali yokken agent'ın kök nedeni ne kadar sürede bulduğunu ölçün. |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-04/solution) | Yapılandırılmış logger, mimari sınır dokümanı ve betiği, düzeltilmiş parçalama mantığı ve [`clean-state-checklist.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/clean-state-checklist.md). | Logların ve sınır kontrollerinin düzeltmeyi hızlandırıp daha az yan etki üretip üretmediğini kontrol edin. |

Özellikle [`projects/project-04/solution/src/services/logger.ts`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/src/services/logger.ts), [`projects/project-04/solution/scripts/check-architecture.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/scripts/check-architecture.sh), [`projects/project-04/solution/docs/ARCHITECTURE.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/docs/ARCHITECTURE.md) ve [`projects/project-04/solution/src/services/indexing-service.ts`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/src/services/indexing-service.ts) dosyalarına bakın.

## Araçlar

- Claude Code veya Codex
- Git
- Node.js + Electron

## Harness Mekanizması

Runtime geri bildirimi + kapsam kontrolü + artımlı dizinleme
