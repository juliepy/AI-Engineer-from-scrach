[中文版本 →](../../../zh/projects/project-06-runtime-observability-and-debugging/)

> İlgili dersler: [Ders 11. Ajanın runtime'ını gözlemlenebilir kılın](./../../lectures/lecture-11-why-observability-belongs-inside-the-harness/index.md) · [Ders 12. Her oturumun sonunda temiz devir](./../../lectures/lecture-12-why-every-session-must-leave-a-clean-state/index.md)
> Şablon dosyaları: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/templates/)

# Proje 06. Eksiksiz bir ajan harness'ı inşa edin (Bitirme Projesi)

## Ne Yapacaksınız

Bu, bitirme projesidir. İlk beş projede öğrendiğiniz her şeyi bir araya getirin, eksiksiz bir kıyaslama çalıştırın, ardından kalitenin sürdürülebilir olduğunu doğrulamak için bir temizlik turu yapın.

Tüm ürün dilimini kapsayan sabit, çok özellikli bir görev seti kullanın: doküman içe aktarma, dizinleme, alıntı tabanlı Soru-Cevap, runtime gözlemlenebilirliği ve okunabilir, yeniden başlatılabilir depo durumu. Önce zayıf harness temeli ile, sonra en güçlü harness'ınızla, ardından bir temizleme ve yeniden çalıştırma. Son olarak bir harness ablation deneyi yapın — bileşenleri tek tek çıkarın ve hangilerinin gerçekten önemli olduğunu görün.

## Depodaki projeyi kullanın

Depo yolu: [`projects/project-06/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-06)

| Dizin | İçerik | Nasıl kullanılır |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-06/starter) | Ürün kodunun çoğu tamamlanmıştır; fakat harness yüzeyi zayıftır: yalnızca temel [`AGENTS.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/starter/AGENTS.md) vardır, `feature_list.json`, `session-handoff.md` ve clean-state checklist yoktur. | Zayıf harness temelini elle kaydedin. Starter kasıtlı olarak benchmark betiği içermez. |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-06/solution) | Tam harness: [`AGENTS.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/AGENTS.md), [`CLAUDE.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/CLAUDE.md), [`feature_list.json`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/feature_list.json), [`init.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/init.sh), [`session-handoff.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/session-handoff.md), [`clean-state-checklist.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/clean-state-checklist.md), kalite/değerlendirme dokümanları, benchmark ve cleanup betikleri. | [`projects/project-06/solution/scripts/benchmark.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/scripts/benchmark.sh) ve [`projects/project-06/solution/scripts/cleanup-scanner.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/scripts/cleanup-scanner.sh) çalıştırın; kalite dokümanı kanıtlarını karşılaştırın. |

Önceki projelerden farklı olarak capstone starter çok sayıda ürün özelliğinden yoksun değildir; ana eksik uygulamanın etrafındaki operasyonel harness'tır.

## Araçlar

- Claude Code veya Codex
- Git
- Node.js + Electron
- Kalite doküman şablonu
- Değerlendirici rubriği
- İlk beş projeden biriktirilen tüm harness bileşenleri

## Harness Mekanizması

Eksiksiz harness: tüm mekanizmalar + gözlemlenebilirlik + ablation çalışması
