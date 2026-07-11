[中文版本 →](../../../zh/projects/project-05-grounded-qa-verification/)

> İlgili dersler: [Ders 09. Ajanların zaferi erken ilan etmesini durdurun](./../../lectures/lecture-09-why-agents-declare-victory-too-early/index.md) · [Ders 10. Yalnızca tam hat çalıştırması gerçek doğrulama sayılır](./../../lectures/lecture-10-why-end-to-end-testing-changes-results/index.md)
> Şablon dosyaları: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/templates/)

# Proje 05. Ajanın kendi işini doğrulamasını sağlayın

## Ne Yapacaksınız

Rol ayrımını uygulayın — uygulamayı yapan bir üretici, inceleyen bir değerlendirici ve isteğe bağlı olarak bir planlayıcı. Eklenen her rolün etkisini ölçmek için üç kez çalıştırın.

Esaslı bir özellik yükseltmesi seçin (çok turlu konuşma, alıntı paneli yeniden tasarımı veya doküman filtreleme) ve tüm çalıştırmalarda tutarlı tutun.

## Depodaki projeyi kullanın

Depo yolu: [`projects/project-05/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05)

| Dizin | İçerik | Nasıl kullanılır |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/starter) | ConversationHistory yükseltmesinden önceki Project 04 uygulaması. | Üç varyantı kendiniz yeniden çalıştırmak istiyorsanız buradan başlayın. |
| [`solution/single-role/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/solution/single-role) | Tek agent planlar, uygular ve kendini değerlendirir. | [`evaluator-rubric.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/single-role/evaluator-rubric.md) içinde 1.6/5 puan ve hata listesi vardır. |
| [`solution/gen-eval/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/solution/gen-eval) | Üretici + değerlendirici; revizyon kanıtı içerir. | [`evaluator-rubric.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/gen-eval/evaluator-rubric.md) içinde 3.3/5 puan ve revizyon kaydı vardır. |
| [`solution/plan-gen-eval/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/solution/plan-gen-eval) | Planlayıcı + üretici + değerlendirici. | [`sprint-contract.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/plan-gen-eval/sprint-contract.md) ve [`evaluator-rubric.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/plan-gen-eval/evaluator-rubric.md) içinde 4.9/5 puan vardır. |

Amaç, aynı ürün yükseltmesini üç farklı harness yapısıyla karşılaştırmaktır; rastgele farklı özellikler seçerseniz puanlar karşılaştırılamaz.

## Araçlar

- Claude Code veya Codex
- Git
- Node.js + Electron

## Harness Mekanizması

Öz-doğrulama + dayanaklı Soru-Cevap + kanıta dayalı tamamlama
